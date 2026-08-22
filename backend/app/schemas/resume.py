"""Phase 3 request and response contracts for resume upload and retrieval."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ParsedResumeData(BaseModel):
    """Deterministically extracted fields; absent data is represented honestly as null or empty lists."""

    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: str
    parsed: ParsedResumeData


class ResumeDetailResponse(ResumeUploadResponse):
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumePersistencePayload(BaseModel):
    """Internal service payload separated from ORM models and HTTP form fields."""

    original_filename: str
    storage_key: str
    content_type: str
    byte_size: int
    checksum_sha256: str
    extracted_text: str
    status: str
    parsed_data: dict[str, Any]
