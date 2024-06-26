import os
import time

import loguru

from uuid import uuid4
from pytube import YouTube
from pydub import AudioSegment
from fastapi import HTTPException, status


def download_youtube_video_as_mp3(url, output_path, max_duration=300, trim_duration=30):
    os.makedirs(output_path, exist_ok=True)
    loguru.logger.debug(url)
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    time.sleep(100)
    video_duration = yt.length
    if video_duration > max_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Длительность видео ({video_duration} секунд) превышает "
                f"максимальную длительность ({max_duration} секунд). Видео не будет загружено."
            ),
        )

    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download(output_path=output_path)

    audio = AudioSegment.from_file(downloaded_file)

    trimmed_audio = audio[: trim_duration * 1000]
    file_name = f"{uuid4()}_trimmed.mp3"
    trimmed_file = os.path.join(output_path, file_name)
    trimmed_audio.export(trimmed_file, format="mp3")

    os.remove(downloaded_file)
    return trimmed_file, file_name
