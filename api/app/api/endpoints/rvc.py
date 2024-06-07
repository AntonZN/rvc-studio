from datetime import datetime

import arrow
from typing import List, Optional, Any

from fastapi import (
    APIRouter,
    status,
)
from pydantic import BaseModel

from app.api import responses


from app.core.config import get_settings

from app.models.rvc import (
    RVCModelSchema,
    RVCModel,
    RVCModelInfo,
    CategorySchema,
    Category,
    ModelProjectUsage,
)

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
    example: Optional[str]
    order: int
    speaker: Optional[str]
    lang: Optional[str]
    gender: Optional[str]
    usages: Optional[int]
    created_at: datetime
    categories: List[Any]


async def get_rvc_model_info_list(project_name):
    rvc_model_infos = (
        await RVCModelInfo.filter(project__name=project_name)
        .order_by("order")
        .prefetch_related("model", "categories")
    )

    result = []

    for rvc_model_info in rvc_model_infos:
        model = rvc_model_info.model

        try:
            print(rvc_model_info.project_id)
            print(model.id)
            print(await ModelProjectUsage.all().values("project_id", "model_id"))
            usages_obj = await ModelProjectUsage.get(
                project_id=rvc_model_info.project_id, model_id=model.id
            )
            usages = usages_obj.usages
        except Exception as e:
            print(e)
            usages = 0

        result.append(
            {
                "id": model.id,
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
                "example": f"{settings.MEDIA_URL}/storage/{rvc_model_info.audio_example}"
                if rvc_model_info.audio_example
                else None,
                "order": rvc_model_info.order,
                "speaker": model.speaker,
                "lang": model.lang,
                "gender": model.gender,
                "created_at": rvc_model_info.created_at,
                "usages": usages,
                "categories": [
                    {"id": category.id, "name": category.name}
                    for category in rvc_model_info.categories
                ],
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
    "/categories/",
    response_model=List[CategorySchema],
    description="Список Категорий",
    responses={
        status.HTTP_404_NOT_FOUND: responses.HTTP_404_NOT_FOUND,
    },
)
async def get_categories_list():
    return await CategorySchema.from_queryset(Category.all().order_by("order"))


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
