"""Unit tests for environment-only database configuration and session factory behavior."""

from collections.abc import Generator

import pytest

from app.core.config import get_settings, normalize_database_url
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


# --- Connection URL normalization ----------------------------------------------------
# Managed PostgreSQL providers hand out driver-less URLs. SQLAlchemy maps a bare
# "postgresql://" to psycopg2, which this project does not install, so pasting a provider
# URL verbatim failed at connect time with ModuleNotFoundError rather than anything that
# pointed at the actual problem.


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("postgresql+psycopg://u:p@h:5432/d", "postgresql+psycopg://u:p@h:5432/d"),
        ("postgresql://u:p@h:5432/d", "postgresql+psycopg://u:p@h:5432/d"),
        ("postgres://u:p@h:5432/d", "postgresql+psycopg://u:p@h:5432/d"),
        ("postgresql://u:p@ep-x.aws.neon.tech/db?sslmode=require", "postgresql+psycopg://u:p@ep-x.aws.neon.tech/db?sslmode=require"),
        ("  postgresql://u:p@h:5432/d\n", "postgresql+psycopg://u:p@h:5432/d"),
        ("'postgresql://u:p@h:5432/d'", "postgresql+psycopg://u:p@h:5432/d"),
        ("postgresql://u:p@h:5432/d\\n", "postgresql+psycopg://u:p@h:5432/d"),
    ],
    ids=["already-psycopg", "driverless", "legacy-postgres-scheme", "provider-url-with-sslmode", "trimmed-provider-url", "quoted-provider-url", "escaped-newline-provider-url"],
)
def test_normalize_database_url_forces_the_installed_driver(raw: str, expected: str) -> None:
    """Only the scheme changes; credentials, host, path, and query must survive intact."""
    assert normalize_database_url(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["sqlite+pysqlite:///:memory:", "mysql://u:p@h/d", "postgresqlish://u:p@h/d", "not-a-url"],
    ids=["sqlite", "mysql", "lookalike-scheme", "garbage"],
)
def test_normalize_database_url_rejects_non_postgresql(raw: str) -> None:
    with pytest.raises(DatabaseConfigurationError, match="PostgreSQL connection scheme"):
        normalize_database_url(raw)


def test_require_database_url_normalizes_a_provider_url(monkeypatch: pytest.MonkeyPatch, isolated_env: None) -> None:
    """A pasted provider URL must reach SQLAlchemy with an explicit psycopg driver."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/d")
    get_settings.cache_clear()

    assert get_settings().require_database_url() == "postgresql+psycopg://u:p@h:5432/d"
