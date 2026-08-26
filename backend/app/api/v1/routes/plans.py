from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.api.v1.dependencies import assert_record_access, get_current_user, get_optional_current_user
from app.db.session import get_db_session
from app.models import MatchResult, ProjectRecommendation, RoadmapItem, User
from app.schemas.plans import CareerPlanResponse, ProjectRecommendationResponse, RoadmapItemResponse, RoadmapItemUpdate
from app.services.planning import build_plan

router = APIRouter(prefix="/plans")


def _as_response(analysis: MatchResult) -> CareerPlanResponse:
    return CareerPlanResponse(
        analysis_id=analysis.id,
        roadmap=[RoadmapItemResponse(id=item.id, skill=item.skill, priority=item.priority, prerequisites=item.prerequisites, sequence=item.sequence, practice_suggestion=item.practice_suggestion, learning_stage=item.learning_stage, completed=item.completed_at is not None) for item in sorted(analysis.roadmap_items, key=lambda item: item.sequence)],
        projects=[ProjectRecommendationResponse(title=item.title, purpose=item.purpose, skills_developed=item.skills_developed, suggested_technology=item.suggested_technology, difficulty=item.difficulty, portfolio_value=item.portfolio_value) for item in analysis.project_recommendations],
    )


@router.post("/{analysis_id}/generate", response_model=CareerPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_plan(analysis_id: UUID, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> CareerPlanResponse:
    analysis = session.get(MatchResult, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    assert_record_access(analysis.resume.user_id, current_user)
    gaps = list((analysis.explanation or {}).get("skill_gaps", []))
    session.execute(delete(RoadmapItem).where(RoadmapItem.match_result_id == analysis_id))
    session.execute(delete(ProjectRecommendation).where(ProjectRecommendation.match_result_id == analysis_id))
    roadmap, projects = build_plan(gaps)
    for item in roadmap:
        item.match_result_id = analysis_id
        session.add(item)
    for project in projects:
        project.match_result_id = analysis_id
        session.add(project)
    session.commit()
    session.refresh(analysis)
    return _as_response(analysis)


@router.patch("/items/{item_id}", response_model=CareerPlanResponse)
def update_roadmap_item(
    item_id: UUID,
    payload: RoadmapItemUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> CareerPlanResponse:
    item = session.get(RoadmapItem, item_id)
    if item is None or item.match_result.resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap item not found.")
    item.completed_at = datetime.now(timezone.utc) if payload.completed else None
    session.commit()
    session.refresh(item.match_result)
    return _as_response(item.match_result)


@router.get("/{analysis_id}", response_model=CareerPlanResponse)
def get_plan(analysis_id: UUID, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> CareerPlanResponse:
    analysis = session.get(MatchResult, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    assert_record_access(analysis.resume.user_id, current_user)
    return _as_response(analysis)
