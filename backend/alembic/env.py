"""Alembic environment configured for environment-supplied PostgreSQL URLs."""

from __future__ import with_statement

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from app.db.base import Base
from app.models import Job, JobSkill, MatchResult, Resume, ResumeSkill, Skill, User  # noqa: F401

# Load backend/.env so Alembic uses the same DATABASE_URL as the FastAPI app when run
# locally. In deployment, real environment variables are already set and take precedence,
# so this line is harmless there.
load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Prefer the deployment environment and retain an inert local Alembic fallback."""
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not make_url(database_url).drivername.startswith("postgresql"):
        raise RuntimeError(
            "DATABASE_URL must use a PostgreSQL connection scheme before Alembic can apply this migration."
        )
    return database_url


def run_migrations_offline() -> None:
    """Generate PostgreSQL SQL without opening a database connection."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations to the PostgreSQL URL supplied through the environment."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
