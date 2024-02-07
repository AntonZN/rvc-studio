import os
from enum import IntEnum, Enum
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
)
from pydantic import BaseModel

from app.core.config import get_settings

from app.models.records import (
    RecordSchema,
    Record,
    RecordStatusSchema,
    Status,
    TTS,
    TTSSchema,
)
from app.core.logic import publish_record

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


def save_file(file):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    record_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(record_path, "wb") as f:
        f.write(file.file.read())

    return record_path


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

    await publish_record("cover", publish_data)

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

    await publish_record("tts", publish_data)

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
