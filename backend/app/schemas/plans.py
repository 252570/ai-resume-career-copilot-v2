from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RoadmapItemResponse(BaseModel):
    id: UUID
    skill: str
    priority: str
    prerequisites: list[str]
    sequence: int
    practice_suggestion: str
    learning_stage: str
    completed: bool = False


class RoadmapItemUpdate(BaseModel):
    completed: bool


class ProjectRecommendationResponse(BaseModel):
    title: str
    purpose: str
    skills_developed: list[str]
    suggested_technology: list[str]
    difficulty: str
    portfolio_value: str


class CareerPlanResponse(BaseModel):
    analysis_id: UUID
    roadmap: list[RoadmapItemResponse] = Field(default_factory=list)
    projects: list[ProjectRecommendationResponse] = Field(default_factory=list)
