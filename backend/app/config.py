from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    backend_host: str = "0.0.0.0"
    backend_port: int = 8001
    content_root: str | None = None
    cors_origins: str = (
        "http://localhost:8765,http://127.0.0.1:8765,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def project_root() -> Path:
    """Repository root (parent of ``backend/``). ``app/config.py`` → ``backend/`` → repo root."""
    return Path(__file__).resolve().parent.parent.parent


def resolve_content_root() -> Path:
    settings = get_settings()
    if settings.content_root:
        return Path(settings.content_root).resolve()
    return (project_root() / "content" / "books").resolve()
