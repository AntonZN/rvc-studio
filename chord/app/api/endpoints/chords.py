import os
import autochord

from typing import List
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
)
from pydantic import BaseModel

from app.core.config import get_settings


settings = get_settings()
router = APIRouter()


class ChordSchema(BaseModel):
    start: float
    end: float
    chord: str


class ResponseSchema(BaseModel):
    file: str
    chords: List[ChordSchema]


def save_file(file):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    record_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(record_path, "wb") as f:
        f.write(file.file.read())

    return record_path


@router.post(
    "/",
    response_model=ResponseSchema,
    description=(
        "Загрузка записи. Используйте `multipart/form-data`. "
        "В ответ получите список аккордов"
    ),
)
async def get_chords(
    file: UploadFile,
):
    record_path = save_file(file)
    lab_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}.lab")
    result = autochord.recognize(record_path, lab_fn=lab_path)
    chords = []

    for chord in result:
        chords.append(ChordSchema(start=chord[0], end=chord[1], chord=chord[2]))

    os.remove(record_path)

    return ResponseSchema(
        file=f"{settings.MEDIA_URL}{lab_path}",
        chords=chords,
    )
