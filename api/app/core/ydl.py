import os
import time
import shutil

import loguru

from uuid import uuid4
from pytube import YouTube
from pydub import AudioSegment
from fastapi import HTTPException, status

from pytube.innertube import _cache_dir


def download_youtube_video_as_mp3(url, output_path, max_duration=300, trim_duration=30):
    os.makedirs(output_path, exist_ok=True)

    try:
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        video_duration = yt.length
    except Exception as e:
        loguru.logger.error(f"Ошибка получения видео: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INCORRECT_LINK",
        )

    if video_duration > max_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INCORRECT_VIDEO_DURATION"
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"DOWNLOAD_ERROR"
    )
    try:
        video = yt.streams.filter(only_audio=True).first()
        downloaded_file = video.download(output_path=output_path)
    except Exception as e:
        loguru.logger.error(f"Ошибка загрузки видео: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOWNLOAD_ERROR"
        )
    try:
        audio = AudioSegment.from_file(downloaded_file)
        trimmed_audio = audio[: trim_duration * 1000]
        file_name = f"{uuid4()}_trimmed.mp3"
        trimmed_file = os.path.join(output_path, file_name)
        trimmed_audio.export(trimmed_file, format="mp3")
    except Exception as e:
        loguru.logger.error(f"Ошибка обработки аудио: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AUDIO_PROCESSING_ERROR"
        )
    finally:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

    return trimmed_file, file_name
