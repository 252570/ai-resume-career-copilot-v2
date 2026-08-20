"""Unit tests for environment-only database configuration and session factory behavior."""

import pytest

from app.core.config import get_settings
from app.core.errors import DatabaseConfigurationError
from app.db.session import get_engine, get_session_factory


def test_database_url_must_be_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()

    with pytest.raises(DatabaseConfigurationError, match="DATABASE_URL is required"):
        get_settings().require_database_url()


def test_database_url_must_use_postgresql(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    get_settings.cache_clear()

    with pytest.raises(DatabaseConfigurationError, match="PostgreSQL connection scheme"):
        get_settings().require_database_url()


def test_session_factory_supports_isolated_test_database() -> None:
    test_url = "sqlite+pysqlite:///:memory:"
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    assert get_engine(test_url).url.drivername == "sqlite+pysqlite"
    assert get_session_factory(test_url).kw["bind"] is get_engine(test_url)
