import json
import os
import warnings
import numpy as np
import torch
import onnxruntime as ort

from tqdm import tqdm
from lib.model_utils import get_hash

from lib.utils import gc_collect

warnings.filterwarnings("ignore")


class MDXParams:
    def __init__(
        self, device, dim_f, dim_t, n_fft, hop=1024, stem_name=None, compensation=1.000
    ):
        self.dim_f = dim_f
        self.dim_t = dim_t
        self.dim_c = 4
        self.n_fft = n_fft
        self.hop = hop
        self.stem_name = stem_name
        self.compensation = compensation

        self.n_bins = self.n_fft // 2 + 1
        self.trim = self.n_fft // 2
        self.chunk_size = hop * (self.dim_t - 1)
        self.device = device
        self.window = torch.hann_window(
            window_length=self.n_fft, periodic=True, device=self.device
        )

        self.freq_pad = torch.zeros(
            [1, self.dim_c, self.n_bins - self.dim_f, self.dim_t]
        ).to(self.device)

        self.gen_size = self.chunk_size - 2 * self.trim

    def stft(self, x):
        x = x.reshape([-1, self.chunk_size])
        x = torch.stft(
            x,
            n_fft=self.n_fft,
            hop_length=self.hop,
            window=self.window,
            center=True,
            return_complex=True,
        )
        x = torch.view_as_real(x)
        x = x.permute([0, 3, 1, 2])
        x = x.reshape([-1, 2, 2, self.n_bins, self.dim_t]).reshape(
            [-1, self.dim_c, self.n_bins, self.dim_t]
        )
        return x[:, :, : self.dim_f]

    def istft(self, x, freq_pad=None):
        freq_pad = (
            self.freq_pad.repeat([x.shape[0], 1, 1, 1])
            if freq_pad is None
            else freq_pad
        )
        x = torch.cat([x, freq_pad], -2)
        x = x.reshape([-1, 2, 2, self.n_bins, self.dim_t]).reshape(
            [-1, 2, self.n_bins, self.dim_t]
        )
        x = x.permute([0, 2, 3, 1])
        x = x.contiguous()
        x = torch.view_as_complex(x)
        x = torch.istft(
            x, n_fft=self.n_fft, hop_length=self.hop, window=self.window, center=True
        )
        return x.reshape([-1, 2, self.chunk_size])


class MDXModel:
    DEFAULT_SR = 44100
    DEFAULT_CHUNK_SIZE = 0 * DEFAULT_SR
    DEFAULT_MARGIN_SIZE = 1 * DEFAULT_SR

    DEFAULT_PROCESSOR = 0

    def __init__(
        self,
        model_path: str,
        device="cpu",
        margin=DEFAULT_MARGIN_SIZE,
        chunks=15,
        denoise=False,
    ):
        self.device = device
        self.providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        mp = self.get_params(model_path)
        self.params = MDXParams(
            self.device,
            dim_f=mp["mdx_dim_f_set"],
            dim_t=2 ** mp["mdx_dim_t_set"],
            n_fft=mp["mdx_n_fft_scale_set"],
            stem_name=mp["primary_stem"],
            compensation=mp["compensate"],
        )

        self.ort = ort.InferenceSession(model_path, providers=self.providers)

        self.run = lambda spec: self.ort.run(None, {"input": spec.cpu().numpy()})[0]
        self.margin = margin
        self.chunks = chunks
        self.denoise = denoise
        self.mdx_batch_size = 1

    def initialize_mix(self, mix, is_ckpt=False):
        if is_ckpt:
            pad = (
                self.params.gen_size
                + self.params.trim
                - ((mix.shape[-1]) % self.params.gen_size)
            )
            mixture = np.concatenate(
                (
                    np.zeros((2, self.params.trim), dtype="float32"),
                    mix,
                    np.zeros((2, pad), dtype="float32"),
                ),
                1,
            )
            num_chunks = mixture.shape[-1] // self.params.gen_size
            mix_waves = [
                mixture[
                    :,
                    i * self.params.gen_size : i * self.params.gen_size
                    + self.params.chunk_size,
                ]
                for i in range(num_chunks)
            ]
        else:
            mix_waves = []
            n_sample = mix.shape[1]
            pad = self.params.gen_size - n_sample % self.params.gen_size
            mix_p = np.concatenate(
                (
                    np.zeros((2, self.params.trim)),
                    mix,
                    np.zeros((2, pad)),
                    np.zeros((2, self.params.trim)),
                ),
                1,
            )
            i = 0
            while i < n_sample + pad:
                waves = np.array(mix_p[:, i : i + self.params.chunk_size])
                mix_waves.append(waves)
                i += self.params.gen_size

        mix_waves = torch.tensor(mix_waves, dtype=torch.float32).to(self.device)

        return mix_waves, pad

    def demix_base(self, mix, is_ckpt=False, is_match_mix=False):
        chunked_sources = []
        for slice in tqdm(mix, "Processing audio:"):
            sources = []
            tar_waves_ = []
            mix_p = mix[slice]
            mix_waves, pad = self.initialize_mix(mix_p, is_ckpt=is_ckpt)
            mix_waves = mix_waves.split(self.mdx_batch_size)
            pad = mix_p.shape[-1] if is_ckpt else -pad

            with torch.no_grad():
                for mix_wave in mix_waves:
                    tar_waves = self.run_model(
                        mix_wave, is_ckpt=is_ckpt, is_match_mix=is_match_mix
                    )
                    tar_waves_.append(tar_waves)
                tar_waves_ = (
                    np.vstack(tar_waves_)[:, :, self.params.trim : -self.params.trim]
                    if is_ckpt
                    else tar_waves_
                )
                tar_waves = np.concatenate(tar_waves_, axis=-1)[:, :pad]
                start = 0 if slice == 0 else self.margin
                end = (
                    None
                    if slice == list(mix.keys())[::-1][0] or self.margin == 0
                    else -self.margin
                )
                sources.append(tar_waves[:, start:end] / self.params.compensation)
            chunked_sources.append(sources)
        sources = np.concatenate(chunked_sources, axis=-1)

        return sources

    def run_model(self, mix, is_ckpt=False, is_match_mix=False):
        spek = self.params.stft(mix.to(self.device)) * self.params.compensation
        spek[:, :, :3, :] *= 0

        if is_match_mix:
            spec_pred = spek.cpu().numpy()
        else:
            spec_pred = (
                self.run(spek) * 0.5 - self.run(-spek) * 0.5
                if self.denoise
                else self.run(spek)
            )

        if is_ckpt:
            return self.params.istft(spec_pred).cpu().detach().numpy()
        else:
            return (
                self.params.istft(torch.tensor(spec_pred).to(self.device))
                .cpu()[:, :, self.params.trim : -self.params.trim]
                .transpose(0, 1)
                .reshape(2, -1)
                .numpy()
            )

    def __del__(self):
        del self.ort
        gc_collect()

    @staticmethod
    def get_params(model_path):
        model_hash = get_hash(model_path)
        with open(
            os.path.join(os.path.dirname(model_path), "model_data.json")
        ) as infile:
            model_params = json.load(infile)

        return model_params.get(model_hash)
