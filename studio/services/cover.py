import loguru

from lib.audio import merge_audio, save_input_audio
from services import check_rvc_model_exists
from services.cloning import clone_for_cover, CloneType
from services.splitter import split_for_cover

from cfg import get_settings

settings = get_settings()


def create_cover(
    record_id, audio_path, model_name, clone_type: int = CloneType.DEFAULT.value
):
    try:
        check_rvc_model_exists(model_name)
        vocal, instrumental = split_for_cover(record_id, audio_path)
        result_path = f"{settings.OUTPUT_FOLDER}/{record_id}/{model_name}.mp3"
        cloned_vocal = clone_for_cover(vocal, model_name, clone_type)
        mixed_audio = merge_audio(cloned_vocal, instrumental, sr=instrumental[1])
        save_input_audio(result_path, mixed_audio)
        return result_path
    except Exception as e:
        loguru.logger.error(e)
