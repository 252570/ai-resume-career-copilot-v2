"""Test fixtures that exercise the models through an isolated in-memory database."""

from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import get_engine, get_session_factory
import app.models  # noqa: F401
from app.security.rate_limit import reset_rate_limit_state


@pytest.fixture(autouse=True)
def reset_auth_rate_limits() -> Generator[None, None, None]:
    reset_rate_limit_state()
    yield
    reset_rate_limit_state()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    database_url = "sqlite+pysqlite:///:memory:"
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = get_session_factory(database_url)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        get_engine.cache_clear()
        get_session_factory.cache_clear()
