from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ApplicationStatus = Literal["saved", "applied", "screening", "interviewing", "offer", "rejected", "withdrawn"]


class JobApplicationCreateRequest(BaseModel):
    job_id: UUID | None = None
    company_name: str = Field(min_length=2, max_length=255)
    role_title: str = Field(min_length=2, max_length=255)
    status: ApplicationStatus = "saved"
    applied_at: datetime | None = None
    next_step_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=5000)


class JobApplicationUpdateRequest(BaseModel):
    status: ApplicationStatus | None = None
    applied_at: datetime | None = None
    next_step_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=5000)


class JobApplicationResponse(JobApplicationCreateRequest):
    id: UUID
    created_at: datetime
    updated_at: datetime


class DashboardResponse(BaseModel):
    resume_count: int
    job_count: int
    application_count: int
    applications_by_status: dict[str, int]
    interviews_in_progress: int
    recent_applications: list[JobApplicationResponse]
