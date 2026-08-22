from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SkillGap(BaseModel):
    skill: str
    requirement_type: str
    priority: str
    job_evidence: str | None = None


class AtsCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class AnalysisRequest(BaseModel):
    resume_id: UUID
    job_id: UUID


class MatchAnalysisResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    match_score: float
    score_breakdown: dict[str, float]
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    partially_matched_areas: list[str] = Field(default_factory=list)
    resume_evidence: dict[str, list[str]] = Field(default_factory=dict)
    ats: dict[str, object]
    skill_gaps: list[SkillGap] = Field(default_factory=list)
    created_at: datetime
