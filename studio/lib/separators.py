from multiprocessing.pool import ThreadPool

from lib.constants import MDX_NET_FREQ_CUT
import numpy as np
from lib.mdx import MDXModel

from lib.audio import remix_audio
import librosa


class MDXNet:
    def __init__(
        self,
        model_path,
        chunks=10,
        denoise=False,
        num_threads=1,
        device="cpu",
        **kwargs
    ):
        self.chunks = chunks
        self.sr = 44100

        self.args = kwargs
        self.denoise = denoise
        self.num_threads = 1

        self.device = device

        self.is_mdx_ckpt = "ckpt" in model_path

        self.model = MDXModel(
            model_path, device=self.device, chunks=self.chunks, margin=self.sr
        )

    def __del__(self):
        del self.model

    def process_audio(self, primary, secondary, target_sr=None):
        target_sr = self.sr if target_sr is None else target_sr
        vocals, instrumental = (
            (secondary, primary)
            if "instrument" in self.model.params.stem_name.lower()
            else (primary, secondary)
        )

        with ThreadPool(2) as pool:
            results = pool.starmap(
                remix_audio,
                [
                    (
                        (instrumental, self.sr),
                        target_sr,
                        False,
                        True,
                        self.sr != target_sr,
                        True,
                    ),
                    (
                        (vocals, self.sr),
                        target_sr,
                        False,
                        True,
                        self.sr != target_sr,
                        True,
                    ),
                ],
            )

        return_dict = {
            "sr": target_sr,
            "instrumentals": results[0],
            "vocals": results[1],
        }

        return return_dict

    def run_inference(self, audio_path):
        mdx_net_cut = True if self.model.params.stem_name in MDX_NET_FREQ_CUT else False
        mix, raw_mix, samplerate = self._prepare_mix(
            audio_path, self.model.chunks, self.model.margin, mdx_net_cut=mdx_net_cut
        )
        wave_processed = self.model.demix_base(mix, is_ckpt=self.is_mdx_ckpt)[0]

        raw_mix = (
            self.model.demix_base(raw_mix, is_match_mix=True)[0]
            if mdx_net_cut
            else raw_mix
        )

        return_dict = self.process_audio(
            primary=wave_processed,
            secondary=(raw_mix - wave_processed),
            target_sr=samplerate,
        )
        return_dict["input_audio"] = (raw_mix, samplerate)

        return return_dict

    def _prepare_mix(self, mix, chunk_set, margin_set, mdx_net_cut=False):
        samplerate = 44100

        if not isinstance(mix, np.ndarray):
            mix, samplerate = librosa.load(mix, mono=False, sr=44100)
        else:
            mix = mix.T

        if mix.ndim == 1:
            mix = np.asfortranarray([mix, mix])

        def get_segmented_mix(chunk_set=chunk_set):
            segmented_mix = {}

            samples = mix.shape[-1]
            margin = margin_set
            chunk_size = chunk_set * 44100
            assert not margin == 0, "margin cannot be zero!"

            if margin > chunk_size:
                margin = chunk_size
            if chunk_set == 0 or samples < chunk_size:
                chunk_size = samples

            counter = -1
            for skip in range(0, samples, chunk_size):
                counter += 1
                s_margin = 0 if counter == 0 else margin
                end = min(skip + chunk_size + margin, samples)
                start = skip - s_margin
                segmented_mix[skip] = mix[:, start:end].copy()
                if end == samples:
                    break

            return segmented_mix

        segmented_mix = get_segmented_mix()
        raw_mix = get_segmented_mix(chunk_set=0) if mdx_net_cut else mix

        return segmented_mix, raw_mix, samplerate
