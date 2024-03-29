import os
import warnings

import loguru
import numpy as np

from lib.separators import MDXNet
from lib.audio import pad_audio, remix_audio, save_input_audio, load_input_audio
from lib.utils import gc_collect, get_optimal_threads
from lib import BASE_MODELS_DIR


from cfg import get_settings

settings = get_settings()
warnings.filterwarnings("ignore")


def _split_audio(
    audio_path,
    device="cpu",
):
    num_threads = max(get_optimal_threads(-1), 1)

    model = MDXNet(
        model_path=os.path.join(BASE_MODELS_DIR, "MDXNET/UVR-MDX-NET-vocal_FT.onnx"),
        denoise=False,
        device=device,
        is_half=device == "cuda",
        use_cache=False,
        num_threads=num_threads,
    )

    result = model.run_inference(audio_path)
    instrumental = result["instrumentals"]
    vocals = result["vocals"]

    gc_collect()

    wav_instrument = []
    wav_vocals = [vocals[0]]

    wav_instrument.append(instrumental[0])
    wav_instrument = np.nanmedian(pad_audio(*wav_instrument), axis=0)
    wav_vocals = np.nanmedian(pad_audio(*wav_vocals), axis=0)

    instrumental = remix_audio(
        (wav_instrument, instrumental[-1]), norm=True, to_int16=True, to_mono=True
    )
    vocal = remix_audio(
        (wav_vocals, vocals[-1]), norm=True, to_int16=True, to_mono=True
    )

    return vocal, instrumental


def split_for_cover(record_id, audio_path):
    os.makedirs(os.path.dirname(settings.SPLITTER_CACHE_DIR), exist_ok=True)
    vocal_cache_path = f"{settings.SPLITTER_CACHE_DIR}/{record_id}/vocal.mp3"
    instrumental_cache_path = (
        f"{settings.SPLITTER_CACHE_DIR}/{record_id}/instrumental.mp3"
    )

    if os.path.isfile(vocal_cache_path) and os.path.isfile(instrumental_cache_path):
        vocal = load_input_audio(vocal_cache_path, 44100)
        instrumental = load_input_audio(instrumental_cache_path, 44100)
        return vocal, instrumental

    vocal, instrumental = _split_audio(audio_path)

    save_input_audio(vocal_cache_path, vocal)
    save_input_audio(instrumental_cache_path, instrumental)

    return vocal, instrumental


def split_only(record_id, audio_path):
    try:
        vocal, instrumental = _split_audio(audio_path)
        vocal_file_path = f"{settings.OUTPUT_FOLDER}/{record_id}/vocal.mp3"
        instrumental_file_path = (
            f"{settings.OUTPUT_FOLDER}/{record_id}/instrumental.mp3"
        )

        save_input_audio(vocal_file_path, vocal)
        save_input_audio(instrumental_file_path, instrumental)
        return vocal_file_path, instrumental_file_path
    except Exception as e:
        loguru.logger.error(e)
