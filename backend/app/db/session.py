"""Lazy PostgreSQL engine and request-scoped SQLAlchemy session lifecycle."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


@lru_cache
def get_engine(database_url: str | None = None) -> Engine:
    """Create a cached engine only when a database-backed operation needs one."""
    resolved_url = database_url or get_settings().require_database_url()
    connect_args: dict[str, object] = {}
    engine_options: dict[str, object] = {}
    if resolved_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if resolved_url.endswith(":memory:"):
            engine_options["poolclass"] = StaticPool
    return create_engine(
        resolved_url,
        connect_args=connect_args,
        echo=get_settings().database_echo,
        future=True,
        pool_pre_ping=not resolved_url.startswith("sqlite"),
        **engine_options,
    )


@lru_cache
def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return a reusable session factory for the configured database URL."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine(database_url), expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a request-scoped session and rollback failed database units of work."""
    session = get_session_factory()()
    try:
        yield session
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
