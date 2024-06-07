import loguru

from lib.audio import merge_audio, save_input_audio
from services import check_rvc_model_exists
from services.cloning import clone_for_cover, CloneType
from services.splitter import split_for_cover, split_for_cover_v2

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


def create_cover_v2(
    record_id, audio_path, model_name, clone_type: int = CloneType.DEFAULT.value
):
    try:
        result_path = f"{settings.OUTPUT_FOLDER}/{record_id}/{model_name}.mp3"
        cloned_file_path = (
            f"{settings.OUTPUT_FOLDER}/{record_id}/{model_name}_vocal.mp3"
        )

        check_rvc_model_exists(model_name)
        vocal, instrumental, instrumental_file_path = split_for_cover_v2(
            record_id, audio_path
        )
        cloned_vocal = clone_for_cover(vocal, model_name, clone_type)
        mixed_audio = merge_audio(cloned_vocal, instrumental, sr=instrumental[1])
        save_input_audio(result_path, mixed_audio)

        save_input_audio(cloned_file_path, cloned_vocal)

        return result_path, cloned_file_path, instrumental_file_path
    except Exception as e:
        loguru.logger.error(e)
