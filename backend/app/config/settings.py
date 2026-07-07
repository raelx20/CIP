from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Constituency Intelligence Platform"
    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str= " "

    BACKEND_CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()