from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobRequirementData(BaseModel):
    job_title: str | None = None
    company_name: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)
    important_keywords: list[str] = Field(default_factory=list)


class JobCreateRequest(BaseModel):
    description: str = Field(min_length=40, max_length=50_000)
    title: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    source_url: HttpUrl | None = None
    user_id: UUID | None = None


class JobResponse(BaseModel):
    id: UUID
    title: str
    company_name: str | None
    description: str
    source_url: str | None
    status: str
    parsed: JobRequirementData
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
