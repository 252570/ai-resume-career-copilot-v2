"""Shared SQLAlchemy declarative base for all persisted models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class used by Alembic to discover application metadata."""
