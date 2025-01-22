import os
import uuid

import loguru
from fastapi import HTTPException
from pydub import AudioSegment
from starlette import status
from yt_dlp import YoutubeDL


def download_youtube_video_as_mp3_new(url, output_path, trim_duration=30):
    os.makedirs(output_path, exist_ok=True)
    filename = uuid.uuid4()

    try:
        ydl_opts = {
            "format": "mp3/bestaudio/best",
            "extractaudio": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "outtmpl": f"{output_path}/{filename}.%(ext)s",
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DOWNLOAD_ERROR",
        )

    downloaded_file = f"{output_path}/{filename}.mp3"

    try:
        audio = AudioSegment.from_file(downloaded_file)
        trimmed_audio = audio[: trim_duration * 1000]
        file_name = f"{uuid.uuid4()}_trimmed.mp3"
        trimmed_file = os.path.join(output_path, file_name)
        trimmed_audio.export(trimmed_file, format="mp3")
    except Exception as e:
        loguru.logger.error(f"Ошибка обработки аудио: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AUDIO_PROCESSING_ERROR",
        )
    finally:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

    return trimmed_file, file_name


download_youtube_video_as_mp3_new(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "./test"
)
