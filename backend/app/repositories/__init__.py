"""Persistence access points; API routes will call these in later phases."""

from app.repositories.career import CareerRepository

__all__ = ["CareerRepository"]
