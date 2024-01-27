from functools import lru_cache
import os

import sys
from pathlib import Path

from cfg import Config


@lru_cache
def load_config():
    return Config()


@lru_cache
def get_cwd():
    cwd = os.getcwd()

    if cwd not in sys.path:
        sys.path.append(cwd)

    return cwd


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_MODELS_DIR = os.path.join(BASE_DIR, "models")
