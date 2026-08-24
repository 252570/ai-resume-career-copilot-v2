"""Unit tests for environment-only database configuration and session factory behavior."""

from collections.abc import Generator

import pytest

from app.core.config import get_settings
from app.core.errors import DatabaseConfigurationError
from app.db.session import get_engine, get_session_factory


@pytest.fixture
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Generator[None, None, None]:
    """Run a config test with no .env file in scope.

    Settings declares env_file=".env", resolved relative to the working directory, so
    monkeypatch.delenv alone cannot prove fail-closed behavior: pydantic-settings still
    reads backend/.env off disk. That made these assertions pass only in CI and fail on
    any developer machine configured for local work. Changing into an empty directory
    removes the file from scope so the absent-configuration path is genuinely exercised.
    """
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_database_url_must_be_configured(monkeypatch: pytest.MonkeyPatch, isolated_env: None) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()

    with pytest.raises(DatabaseConfigurationError, match="DATABASE_URL is required"):
        get_settings().require_database_url()


def test_database_url_must_use_postgresql(monkeypatch: pytest.MonkeyPatch, isolated_env: None) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    get_settings.cache_clear()

    with pytest.raises(DatabaseConfigurationError, match="PostgreSQL connection scheme"):
        get_settings().require_database_url()


def test_jwt_secret_must_be_present_and_long_enough(monkeypatch: pytest.MonkeyPatch, isolated_env: None) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    get_settings.cache_clear()
    with pytest.raises(DatabaseConfigurationError, match="JWT_SECRET"):
        get_settings().require_jwt_secret()

    monkeypatch.setenv("JWT_SECRET", "too-short")
    get_settings.cache_clear()
    with pytest.raises(DatabaseConfigurationError, match="at least 32 characters"):
        get_settings().require_jwt_secret()


def test_session_factory_supports_isolated_test_database() -> None:
    test_url = "sqlite+pysqlite:///:memory:"
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    assert get_engine(test_url).url.drivername == "sqlite+pysqlite"
    assert get_session_factory(test_url).kw["bind"] is get_engine(test_url)
