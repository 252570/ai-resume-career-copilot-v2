from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewSessionCreateRequest(BaseModel):
    resume_id: UUID | None = None
    job_id: UUID | None = None
    question_count: int = Field(default=5, ge=3, le=8)


class InterviewQuestion(BaseModel):
    index: int
    category: str
    prompt: str
    focus_skill: str | None = None


class InterviewResponseCreateRequest(BaseModel):
    question_index: int = Field(ge=0)
    answer: str = Field(min_length=20, max_length=6000)


class InterviewAnswerFeedback(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: list[str]
    improvements: list[str]
    disclaimer: str


class InterviewResponseDetail(BaseModel):
    question_index: int
    answer: str
    feedback: InterviewAnswerFeedback


class InterviewSessionResponse(BaseModel):
    id: UUID
    title: str
    status: str
    questions: list[InterviewQuestion]
    responses: list[InterviewResponseDetail]
    created_at: datetime
