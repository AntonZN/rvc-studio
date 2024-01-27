import torch
from multiprocessing import cpu_count
from pathlib import Path
import os
from functools import lru_cache
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseSettings, validator, PostgresDsn


load_dotenv()


class Config:
    def __init__(self):
        self.device = "cpu"
        self.instead = None
        self.is_half = True
        self.n_cpu = 0
        self.gpu_name = None
        self.gpu_mem = None
        self.x_pad, self.x_query, self.x_center, self.x_max = self.device_config()

    @staticmethod
    def use_fp32_config():
        for config_file in [
            "32k.json",
            "40k.json",
            "48k.json",
            "48k_v2.json",
            "32k_v2.json",
        ]:
            with open(
                Path(__file__).resolve().parent / f"configs/{config_file}", "r"
            ) as f:
                string = f.read().replace("true", "false")

            with open(
                Path(__file__).resolve().parent / f"configs/{config_file}", "w"
            ) as f:
                f.write(string)

    @staticmethod
    def has_mps() -> bool:
        if not torch.backends.mps.is_available():
            return False
        try:
            torch.zeros(1).to(torch.device("mps"))
            return True
        except Exception:
            return False

    def device_config(self) -> tuple:
        self.device = self.instead = "cpu"
        self.is_half = False
        self.use_fp32_config()

        if self.n_cpu == 0:
            self.n_cpu = cpu_count()

        if self.is_half:
            x_pad = 3
            x_query = 10
            x_center = 60
            x_max = 64
        else:
            x_pad = 1
            x_query = 6
            x_center = 38
            x_max = 41

        if self.gpu_mem is not None and self.gpu_mem <= 4:
            x_pad = 1
            x_query = 5
            x_center = 30
            x_max = 32

        return x_pad, x_query, x_center, x_max


class Settings(BaseSettings):
    DEBUG: bool = True
    STORAGE_FOLDER: str = "/storage"
    OUTPUT_FOLDER: str = os.path.join(STORAGE_FOLDER, "output")
    RVC_MODELS_FOLDER: str = os.path.join(STORAGE_FOLDER, "models/RVC")
    BASE_CACHE_DIR: str = os.path.join(STORAGE_FOLDER, "cache")
    SPLITTER_CACHE_DIR: str = os.path.join(BASE_CACHE_DIR, "splitter")
    CONSUMERS: int = 5
    APNS_CERT: Optional[str] = None
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_ROUTING_KEY: str = "studio"

    POSTGRES_SCHEME: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        postgres = PostgresDsn.build(
            scheme=values.get("POSTGRES_SCHEME"),
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

        return postgres

    class Config:
        env_file = "./.env"


@lru_cache()
def get_settings():
    return Settings()
