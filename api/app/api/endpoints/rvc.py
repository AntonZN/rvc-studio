from typing import List, Optional

from fastapi import (
    APIRouter,
    status,
)
from pydantic import BaseModel

from app.api import responses


from app.core.config import get_settings

from app.models.rvc import RVCModelSchema, RVCModel, RVCModelInfo

settings = get_settings()
router = APIRouter()


class RVCModelInfoSchema(BaseModel):
    id: int
    ru: Optional[str]
    en: Optional[str]
    es: Optional[str]
    pt: Optional[str]
    fr: Optional[str]
    hi: Optional[str]
    ko: Optional[str]
    description: Optional[str]
    lock: bool
    hide: bool
    image: Optional[str]
    order: int
    speaker: Optional[str]
    lang: Optional[str]
    gender: Optional[str]


async def get_rvc_model_info_list(project_name):
    rvc_model_infos = (
        await RVCModelInfo.filter(project__name=project_name)
        .order_by("order")
        .prefetch_related("model")
    )

    result = []

    for rvc_model_info in rvc_model_infos:
        model = rvc_model_info.model
        result.append(
            {
                "id": rvc_model_info.id,
                "ru": rvc_model_info.ru,
                "en": rvc_model_info.en,
                "es": rvc_model_info.es,
                "pt": rvc_model_info.pt,
                "fr": rvc_model_info.fr,
                "hi": rvc_model_info.hi,
                "ko": rvc_model_info.ko,
                "description": rvc_model_info.description,
                "lock": rvc_model_info.lock,
                "hide": rvc_model_info.hide,
                "image": str(rvc_model_info.image) if rvc_model_info.image else None,
                "order": rvc_model_info.order,
                "speaker": model.speaker,
                "lang": model.lang,
                "gender": model.gender,
            }
        )

    return result


@router.get(
    "/models/",
    response_model=List[RVCModelSchema],
    description="Список доступных RVC моделей",
    responses={
        status.HTTP_404_NOT_FOUND: responses.HTTP_404_NOT_FOUND,
    },
)
async def get_rvc_list():
    return await RVCModelSchema.from_queryset(RVCModel.all())


@router.get(
    "/models/project/{project_name}/",
    response_model=List[RVCModelInfoSchema],
    description="Список доступных RVC моделей для проекта",
    responses={
        status.HTTP_404_NOT_FOUND: responses.HTTP_404_NOT_FOUND,
    },
)
async def get_rvc_list_for_project(project_name):
    return await get_rvc_model_info_list(project_name)
