"""Pydantic request and response contracts; intentionally separate from SQLAlchemy ORM models."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ORMReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str = Field(max_length=320)
    display_name: str = Field(min_length=1, max_length=120)
    profile_headline: str | None = Field(default=None, max_length=255)


class UserRead(ORMReadModel):
    id: UUID
    email: str
    display_name: str
    profile_headline: str | None
    created_at: datetime
    updated_at: datetime


class ResumeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    original_filename: str | None = Field(default=None, max_length=255)
    storage_key: str | None = Field(default=None, max_length=512)
    content_type: str | None = Field(default=None, max_length=127)
    byte_size: int | None = Field(default=None, ge=0)
    checksum_sha256: str | None = Field(default=None, min_length=64, max_length=64)


class ResumeRead(ORMReadModel):
    id: UUID
    user_id: UUID
    title: str
    original_filename: str | None
    storage_key: str | None
    content_type: str | None
    byte_size: int | None
    checksum_sha256: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=255)
    employment_type: str | None = Field(default=None, max_length=64)


class JobRead(ORMReadModel):
    id: UUID
    user_id: UUID | None
    title: str
    company_name: str | None
    description: str
    source_url: str | None
    location: str | None
    employment_type: str | None
    created_at: datetime
    updated_at: datetime


class SkillCreate(BaseModel):
    canonical_name: str = Field(min_length=1, max_length=160)
    category: str | None = Field(default=None, max_length=120)
    description: str | None = None


class SkillRead(ORMReadModel):
    id: UUID
    canonical_name: str
    category: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class ResumeSkillCreate(BaseModel):
    skill_id: UUID
    proficiency_level: int | None = Field(default=None, ge=1, le=5)
    years_experience: Decimal | None = Field(default=None, ge=0, max_digits=4, decimal_places=1)
    is_primary: bool = False
    evidence: str | None = None


class ResumeSkillRead(ORMReadModel):
    resume_id: UUID
    skill_id: UUID
    proficiency_level: int | None
    years_experience: Decimal | None
    is_primary: bool
    evidence: str | None


class JobSkillCreate(BaseModel):
    skill_id: UUID
    importance_level: int = Field(default=3, ge=1, le=5)
    is_required: bool = True
    evidence: str | None = None


class JobSkillRead(ORMReadModel):
    job_id: UUID
    skill_id: UUID
    importance_level: int
    is_required: bool
    evidence: str | None


class MatchResultRead(ORMReadModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    analysis_version: int
    match_score: Decimal | None
    status: str
    explanation: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
