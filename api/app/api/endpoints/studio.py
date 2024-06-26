import datetime
import os
from enum import IntEnum, Enum
from typing import Annotated, Optional
from uuid import uuid4

import loguru
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
)
from pydantic import BaseModel
from tortoise.expressions import F

from app.core.config import get_settings

from app.models.records import (
    RecordSchema,
    Record,
    RecordStatusSchema,
    Status,
    TTS,
    TTSSchema,
    ProcessRequest,
    Statistics,
)
from app.core.logic import publish_record
from app.models.rvc import ModelProjectUsage
from app.core.ydl import download_youtube_video_as_mp3

settings = get_settings()
router = APIRouter()


class Lang(str, Enum):
    RU: str = "ru"
    DE: str = "de"
    EN: str = "en"
    ES: str = "es"
    FR: str = "fr"
    HI: str = "hi"
    IT: str = "it"
    JA: str = "ja"
    KO: str = "ko"
    PL: str = "pl"
    PT: str = "pt"
    TR: str = "tr"
    ZH: str = "zh"


class Speaker(str, Enum):
    NULL: str = "0"
    ONE: str = "1"
    TWO: str = "2"
    FRE: str = "3"
    FOUR: str = "4"
    FIVE: str = "5"
    SIX: str = "6"
    SEVEN: str = "7"
    EIGHT: str = "8"
    NINE: str = "9"


class CloneType(IntEnum):
    DEFAULT = 0
    MALE_TO_FEMALE = 1
    FEMALE_TO_MALE = 2


class CoverBody(BaseModel):
    clone_type: CloneType = Form(alias="cloneType", default=CloneType.DEFAULT)
    model_id: int = Form(alias="modelId")


class TTSBody(BaseModel):
    text: str = Form(alias="text", max_length=220)
    model_id: int = Form(alias="modelId")
    lang: Lang = Lang.EN
    speaker: Optional[Speaker] = Speaker.NULL


class CoverFromUrl(BaseModel):
    url: str
    clone_type: CloneType = Form(alias="cloneType", default=CloneType.DEFAULT)
    model_id: int = Form(alias="modelId")


def save_file(file):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    record_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(record_path, "wb") as f:
        f.write(file.file.read())

    return record_path


async def create_statistics(process):
    try:
        date = datetime.date.today()
        try:
            stat = await Statistics.get(date=date)
        except:
            stat = await Statistics.create(
                date=date,
                count_tts=0,
                count_split=0,
                count_split_old=0,
                count_cover=0,
                count_clone=0,
                average_waiting="неизвестно",
            )

        if process == "tts":
            stat.count_tts += 1
        elif process == "split":
            stat.count_split += 1
        elif process == "old_split":
            stat.count_split_old += 1
        elif process == "cover":
            stat.count_cover += 1
        elif process == "clone":
            stat.count_clone += 1

        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        end_of_day = datetime.datetime.combine(date, datetime.time.max)

        times = (
            await ProcessRequest.filter(
                created_at__gte=start_of_day, created_at__lte=end_of_day
            )
            .exclude(process_type="old_split")
            .values_list("waiting_time_in_seconds", flat=True)
        )

        time_waiting = list(times)

        if time_waiting:  # Check if the list is not empty
            average_time_waiting = sum(time_waiting) / len(time_waiting)
            minutes = average_time_waiting // 60
            remaining_seconds = average_time_waiting % 60
            average_time_waiting = f"{int(minutes)} min {int(remaining_seconds)} sec"
        else:
            average_time_waiting = "0"

        stat.average_waiting = average_time_waiting

        await stat.save()
    except Exception as e:
        loguru.logger.error(e)


@router.post(
    "/split/",
    response_model=RecordSchema,
    description=(
        "Загрузка записи. Используйте `multipart/form-data`. "
        "В ответ получите `id` записи по которому можно проверить статус"
    ),
)
async def split_record(
    file: Annotated[UploadFile, File()],
):
    record_path = save_file(file)
    record = await Record.create(name=file.filename, file_path=record_path)

    publish_data = {
        "record_id": str(record.id),
    }

    await publish_record("split", publish_data)
    await create_statistics("split")

    return record


@router.post(
    "/clone_voice/",
    response_model=RecordSchema,
    description=(
        "Загрузка для клонирования голосоа в персонажа. Используйте `multipart/form-data`. "
        "В ответ получите `id` записи по которому можно проверить статус"
        "`cloneType` - тип клонирования, 0 - по умолчанию, 1 - мужчина в женщину, 3 - женщина в мужчину"
    ),
)
async def clone_voice(
    file: Annotated[UploadFile, File()],
    model_id: Annotated[int, Form(alias="modelId")],
    clone_type: Annotated[
        CloneType, int, Form(alias="cloneType")
    ] = CloneType.DEFAULT.value,
):
    record_path = save_file(file)
    record = await Record.create(name=file.filename, file_path=record_path)

    publish_data = {
        "record_id": str(record.id),
        "model_id": model_id,
        "type": clone_type,
    }
    await publish_record("clone", publish_data)
    await create_statistics("clone")
    return record


@router.post(
    "/cover/",
    response_model=RecordSchema,
    description=(
        "Загрузка записи. Используйте `multipart/form-data`. "
        "В ответ получите `id` записи по которому можно использовать studio"
        "`cloneType` - тип клонирования, 0 - по умолчанию, 1 - мужчина в женщину, 3 - женщина в мужчину"
    ),
)
async def cover(
    file: Annotated[UploadFile, File()],
    model_id: Annotated[int, Form(alias="modelId")],
    clone_type: Annotated[
        CloneType, int, Form(alias="cloneType")
    ] = CloneType.DEFAULT.value,
):
    record_path = save_file(file)
    record = await Record.create(name=file.filename, file_path=record_path)

    publish_data = {
        "record_id": str(record.id),
        "model_id": model_id,
        "type": clone_type,
    }
    if await ModelProjectUsage.filter(project_id=3, model_id=model_id).exists():
        await ModelProjectUsage.filter(project_id=3, model_id=model_id).update(
            usages=F("usages") + 1
        )
    else:
        await ModelProjectUsage.create(project_id=3, model_id=model_id, usages=1)

    await publish_record("cover", publish_data)
    await create_statistics("cover")

    return record


@router.post(
    "/cover_from_url/",
    response_model=RecordSchema,
    description=(
        "Загрузка записи. Используйте `multipart/form-data`. "
        "В ответ получите `id` записи по которому можно использовать studio"
        "`cloneType` - тип клонирования, 0 - по умолчанию, 1 - мужчина в женщину, 3 - женщина в мужчину"
    ),
)
async def cover_from_url(body: CoverFromUrl):
    record_path, filename = download_youtube_video_as_mp3(
        body.url,
        settings.UPLOAD_FOLDER,
        max_duration=300,
        trim_duration=30,
    )
    loguru.logger.debug(f"YOUTUBE {record_path}, {filename}")
    record = await Record.create(name=filename, file_path=record_path)

    publish_data = {
        "record_id": str(record.id),
        "model_id": body.model_id,
        "type": body.clone_type,
    }
    if await ModelProjectUsage.filter(project_id=3, model_id=body.model_id).exists():
        await ModelProjectUsage.filter(project_id=3, model_id=body.model_id).update(
            usages=F("usages") + 1
        )
    else:
        await ModelProjectUsage.create(project_id=3, model_id=body.model_id, usages=1)

    await publish_record("cover", publish_data)
    await create_statistics("cover")

    return record


@router.post(
    "/tts/",
    response_model=TTSSchema,
    description="Текст в речь",
)
async def create_tts(body: TTSBody):
    tts = await TTS.create()

    text = body.text.replace("\n", " ").strip()

    publish_data = {
        "text": text,
        "tts_id": str(tts.id),
        "model_id": body.model_id,
        "lang": body.lang.value,
        "speaker": body.speaker.value,
    }
    if await ModelProjectUsage.filter(project_id=1, model_id=body.model_id).exists():
        await ModelProjectUsage.filter(project_id=1, model_id=body.model_id).update(
            usages=F("usages") + 1
        )
    else:
        await ModelProjectUsage.create(project_id=1, model_id=body.model_id, usages=1)
    await publish_record("tts", publish_data)
    await create_statistics("tts")
    return tts


@router.get(
    "/record/{record_id}/",
    response_model=RecordStatusSchema,
    description="Статус и результат обработки записи",
)
async def record_status(record_id: str):
    record = await Record.get(id=record_id)
    paths_to_update = ["vocal_path", "instrumental_path", "clone_path", "cover_path"]

    for path in paths_to_update:
        if getattr(record, path):
            setattr(record, path, f"{settings.MEDIA_URL}{getattr(record, path)}")

    return record


@router.put(
    "/record/{record_id}/cancel/",
    response_model=TTSSchema,
    description="Отменить обработку записи",
)
async def tts_cancel(record_id: str):
    record = await Record.get(id=record_id)
    record.status = Status.CANCELED
    await record.save()
    return record


@router.get(
    "/tts/{tts_id}/",
    response_model=TTSSchema,
    description="Статус и результат обработки TTS",
)
async def tts_status(tts_id: str):
    tts = await TTS.get(id=tts_id)

    if tts.voice_path:
        tts.voice_path = f"{settings.MEDIA_URL}{tts.voice_path}"

    return tts


@router.put(
    "/tts/{tts_id}/cancel/",
    response_model=TTSSchema,
    description="Отменить TTS",
)
async def tts_cancel(tts_id: str):
    tts = await TTS.get(id=tts_id)
    tts.status = Status.CANCELED
    await tts.save()
    return tts


@router.post(
    "/record/{record_id}/cover/",
    response_model=RecordSchema,
    description="Сделать cover уже загруженной песни",
)
async def record_status(record_id: str, body: CoverBody):
    record = await Record.get(id=record_id)
    record.status = Status.PENDING
    await record.save()

    publish_data = {
        "record_id": record_id,
        "model_id": body.model_id,
        "type": body.clone_type,
    }

    await publish_record("cover", publish_data)

    return record


@router.get(
    "/statistics/",
    description="Статистика",
)
async def get_statistics():
    all_use_count = await ProcessRequest.all().count()
    tts_use_count = await ProcessRequest.filter(process_type="tts").count()
    cover_use_count = await ProcessRequest.filter(process_type="cover").count()
    clone_use_count = await ProcessRequest.filter(process_type="clone").count()
    split_use_count = await ProcessRequest.filter(process_type="split").count()
    times = (
        await ProcessRequest.all()
        .exclude(process_type="old_split")
        .values_list("waiting_time_in_seconds", flat=True)
    )
    time_waiting = list(times)

    try:
        average_time_waiting = sum(time_waiting) / len(time_waiting)
        minutes = average_time_waiting // 60
        remaining_seconds = average_time_waiting % 60
        average_time_waiting = f"{int(minutes)} мин {int(remaining_seconds)} сек"
    except ZeroDivisionError:
        average_time_waiting = 0

    return dict(
        use_count=all_use_count,
        tts_use_count=tts_use_count,
        cover_use_count=cover_use_count,
        clone_use_count=clone_use_count,
        split_use_count=split_use_count,
        average_time_waiting=average_time_waiting,
    )


@router.post(
    "/statistics/old_split/",
)
async def old_split():
    await create_statistics("old_split")


@router.post(
    "/statistics/old_split/avg/",
)
async def old_split(seconds: int):
    await ProcessRequest.create(
        process_type="old_split", waiting_time_in_seconds=seconds
    )
