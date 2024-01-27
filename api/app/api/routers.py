from fastapi import APIRouter, Depends
from starlette import status

from app.api import responses
from app.api.endpoints import rvc, studio
from app.core.deps import token_validation

router = APIRouter(
    dependencies=[Depends(token_validation)],
    responses={
        status.HTTP_401_UNAUTHORIZED: responses.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: responses.HTTP_403_FORBIDDEN,
    },
)

router.include_router(rvc.router, tags=["RVC"], prefix="/rvc")
router.include_router(studio.router, tags=["STUDIO"], prefix="/studio")
