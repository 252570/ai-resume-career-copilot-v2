"""Validated environment configuration; secrets never belong in source code."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.errors import DatabaseConfigurationError


class Settings(BaseSettings):
    """Runtime settings with safe defaults and environment-only database credentials."""

    app_name: str = "AI Resume & Career Copilot API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    database_echo: bool = False
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    resume_storage_dir: Path = Path("storage/resumes")
    max_resume_upload_bytes: int = 5 * 1024 * 1024
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def require_database_url(self) -> str:
        """Return the PostgreSQL URL or raise a safe, actionable configuration error."""
        if not self.database_url:
            raise DatabaseConfigurationError(
                "DATABASE_URL is required for database-backed operations. "
                "Set it in the runtime environment before running migrations or the API."
            )
        if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise DatabaseConfigurationError("DATABASE_URL must use a PostgreSQL connection scheme.")
        return self.database_url

    def allowed_cors_origins(self) -> list[str]:
        """Return a non-empty, explicitly configured CORS origin list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def require_jwt_secret(self) -> str:
        if not self.jwt_secret or len(self.jwt_secret) < 32:
            raise DatabaseConfigurationError("JWT_SECRET must be set to a secure value of at least 32 characters.")
        return self.jwt_secret


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated configuration object."""
    return Settings()
