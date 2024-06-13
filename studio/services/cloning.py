import os

from enum import IntEnum

import librosa
import numpy as np

from lib.audio import save_input_audio, load_input_audio
import soundfile as sf
from lib.vc_infer_pipeline import get_vc, vc_single
from services.errors import RVCModelLoadError
from cfg import get_settings

settings = get_settings()


class CloneType(IntEnum):
    DEFAULT = 0
    MALE_TO_FEMALE = 1
    FEMALE_TO_MALE = 2


def clone_vocal(
    vocal,
    model_name: str,
    clone_type: int = CloneType.DEFAULT.value,
):
    def load_model(name: str):
        from cfg import Config

        config = Config()

        try:
            path = os.path.join(settings.RVC_MODELS_FOLDER, f"{name}.pth")
            return get_vc(path, config)
        except Exception as e:
            raise RVCModelLoadError(e)

    f0_up_keys = {
        CloneType.DEFAULT.value: 0,
        CloneType.FEMALE_TO_MALE: -5,
        CloneType.MALE_TO_FEMALE: 5,
    }

    params = {
        "f0_up_key": f0_up_keys[clone_type],
        "f0_method": ["rmvpe"],
        "f0_autotune": False,
        "merge_type": "median",
        "index_rate": 0.75,
        "resample_sr": 44100,
        "rms_mix_rate": 0.2,
        "protect": 0.2,
    }

    if model := load_model(model_name):
        output_audio = vc_single(input_audio=vocal, **model, **params)
        return output_audio
    else:
        print("HUI")


def clone_for_cover(
    vocal,
    model_name,
    clone_type: int = CloneType.DEFAULT.value,
):
    return clone_vocal(vocal, model_name, clone_type)


def clone_only(
    record_id,
    audio_path,
    model_name,
    clone_type=CloneType.DEFAULT.value,
):
    cloned_file_path = f"{settings.OUTPUT_FOLDER}/{record_id}/{model_name}.mp3"
    vocal = librosa.load(audio_path, mono=True, sr=44100)

    cloned_vocal = clone_vocal(vocal, model_name, clone_type)
    os.makedirs(os.path.dirname(cloned_file_path), exist_ok=True)
    sf.write(cloned_file_path, cloned_vocal, 44100)

    return cloned_file_path
