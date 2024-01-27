import os

from services.errors import RVCModelDoesNotExists
from cfg import get_settings

settings = get_settings()


def check_rvc_model_exists(model_name):
    if not os.path.isfile(
        os.path.join(settings.RVC_MODELS_FOLDER, f"{model_name}.pth")
    ):
        raise RVCModelDoesNotExists(f"Model {model_name} not exists")
