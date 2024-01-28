import base64
import zlib

import loguru
import numpy as np

from lib import BASE_MODELS_DIR
from lib.audio import save_input_audio, MAX_INT16

import os
from services.cloning import clone_vocal
from transformers import BarkModel, BarkProcessor
from cfg import get_settings


settings = get_settings()


def audio2bytes(audio: np.array, sr: int):
    try:
        dtype = audio.dtype.name
        shape = audio.shape
        data = audio.tobytes()
        compressed_data = zlib.compress(data)
        encoded_data = base64.b64encode(compressed_data)
        suffixed_data = ":".join(
            [dtype, encoded_data.decode(), ",".join(map(str, shape)), str(sr)]
        )
        return suffixed_data
    except Exception as e:
        print(e)
    return ""


def bytes2audio(data: str):
    try:
        dtype, data, shape, sr = data.split(":")
        shape = tuple(map(int, shape.split(",")))
        sr = int(sr)
        decoded_data = base64.b64decode(data)
        decompressed_data = zlib.decompress(decoded_data)
        arr = np.frombuffer(decompressed_data, dtype=dtype)
        arr = arr.reshape(shape)
        return arr, sr
    except Exception as e:
        print(e)
    return None


def tts(tts_id, model_name, text: str, lang: str, speaker=0):
    loguru.logger.debug("START TTS")
    result_filepath = f"{settings.OUTPUT_FOLDER}/{tts_id}/{model_name}.mp3"
    model = BarkModel.from_pretrained(f"{BASE_MODELS_DIR}/bark-small")
    processor = BarkProcessor.from_pretrained(f"{BASE_MODELS_DIR}/bark-small")
    inputs = processor(text, voice_preset=f"v2/{lang}_speaker_{speaker}")
    attention_mask = inputs.ne(processor.pad_token_id)
    speech_output = (
        model.generate(**inputs, attention_mask=attention_mask).cpu().numpy().squeeze()
        * MAX_INT16
    ).astype(np.int16)
    sampling_rate = model.generation_config.sample_rate
    audio_data = audio2bytes(speech_output, sr=sampling_rate)
    output_audio = clone_vocal(bytes2audio(audio_data), model_name)
    save_input_audio(result_filepath, output_audio)

    return result_filepath
