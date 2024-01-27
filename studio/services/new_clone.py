import os

from lib import BASE_MODELS_DIR, OUTPUT_DIR
from enum import IntEnum

from lib.audio import save_input_audio, load_input_audio
from lib.vc_infer_pipeline import get_vc, vc_single
from services.errors import RVCModelLoadError


class CloneType(IntEnum):
    DEFAULT = 0
    MALE_TO_FEMALE = 1
    FEMALE_TO_MALE = 2


def clone_vocal(
    vocal,
    model_name: str,
    clone_type: CloneType = CloneType.DEFAULT,
):
    def load_model(name: str):
        from cfg import Config

        config = Config()

        try:
            path = os.path.join(BASE_MODELS_DIR, "RVC", f"{name}.pth")
            return get_vc(path, config)
        except Exception as e:
            raise RVCModelLoadError(e)

    f0_up_keys = {
        CloneType.DEFAULT.value: 0,
        CloneType.FEMALE_TO_MALE: -5,
        CloneType.MALE_TO_FEMALE: 5,
    }

    params = {
        "f0_up_key": f0_up_keys[clone_type.value],
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


def clone_for_cover(
    vocal,
    model_name: str,
    clone_type: CloneType = CloneType.DEFAULT,
):
    return clone_vocal(vocal, model_name, clone_type)


def clone_only(
    audio_path,
    model_name: str,
    clone_type: CloneType = CloneType.DEFAULT,
):
    song_id = os.path.basename(audio_path).split(".")[0]
    cloned_file_path = f"{OUTPUT_DIR}/{song_id}/cloned.mp3"
    vocal = load_input_audio(audio_path, 44100)
    cloned_vocal = clone_vocal(vocal, model_name, clone_type)

    save_input_audio(cloned_file_path, cloned_vocal)

    return cloned_file_path
