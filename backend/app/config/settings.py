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

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/cip"

    JWT_SECRET_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000", "http://localhost:5173"]

    # LLM Configuration
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_API_KEY: str = "ollama"
    LLM_MODEL: str = "qwen3:1.7b"
    LLM_TIMEOUT: int = 120
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # Geospatial
    GOOGLE_MAPS_API_KEY: str = ""

    @property
    def sync_database_url(self) -> str:
        """Synchronous database URL for Alembic migrations."""
        url = self.DATABASE_URL
        # Convert async driver to sync for Alembic
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        url = url.replace("postgresql+psycopg_async://", "postgresql://")
        return url

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