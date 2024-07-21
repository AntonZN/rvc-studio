from pytube import cipher
import re

from pytube.exceptions import RegexMatchError


def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r"\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)",
        r"\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)",
    ]
    # logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            # logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r"var {nfunc}\s*=\s*(\[.+?\]);".format(
                        nfunc=re.escape(function_match.group(1))
                    ),
                    js,
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise RegexMatchError(caller="get_throttling_function_name", pattern="multiple")


cipher.get_throttling_function_name = get_throttling_function_name

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
            status_code=status.HTTP_400_BAD_REQUEST, detail="INCORRECT_VIDEO_DURATION"
        )

    try:
        video = yt.streams.filter(only_audio=True).first()
        downloaded_file = video.download(output_path=output_path)
    except Exception as e:
        loguru.logger.error(f"Ошибка загрузки видео: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DOWNLOAD_ERROR"
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
            detail=f"AUDIO_PROCESSING_ERROR",
        )
    finally:
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

    return trimmed_file, file_name
