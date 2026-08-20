"""Validated environment configuration; secrets never belong in source code."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings with safe Phase 1 defaults."""

    app_name: str = "AI Resume & Career Copilot API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated configuration object."""
    return Settings()
