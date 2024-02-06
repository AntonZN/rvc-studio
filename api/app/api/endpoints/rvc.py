from typing import List

from fastapi import (
    APIRouter,
    status,
)
from app.api import responses


from app.core.config import get_settings

from app.models.rvc import RVCModelSchema, RVCModel

settings = get_settings()
router = APIRouter()


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
