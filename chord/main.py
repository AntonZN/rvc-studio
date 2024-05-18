import sys
import warnings

from fastapi import FastAPI, logger

from app.api.routers import router
from app.core.config import get_settings

warnings.filterwarnings("ignore")

settings = get_settings()

logger.logger.setLevel(level=settings.LOG_LEVEL)

app = FastAPI(
    docs_url="/chords/docs", redoc_url=None, openapi_url="/chords/openapi.json"
)
app.include_router(router, prefix="/chords/api/v1")


if settings.DEBUG:
    import logging

    fmt = logging.Formatter(
        fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt)

    logger_db_client = logging.getLogger("tortoise.db_client")
    logger_db_client.setLevel(logging.DEBUG)
    logger_db_client.addHandler(sh)
