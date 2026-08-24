from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import assert_record_access, get_optional_current_user
from app.db.session import get_db_session
from app.models import MatchResult, User
from app.repositories.career import CareerRepository
from app.schemas.analysis import AnalysisRequest, MatchAnalysisResponse, SkillGap
from app.services.matching import analyze_resume_job

router = APIRouter(prefix="/analyses")


def _as_response(result: MatchResult) -> MatchAnalysisResponse:
    explanation = result.explanation or {}
    return MatchAnalysisResponse(
        id=result.id, resume_id=result.resume_id, job_id=result.job_id, match_score=float(result.match_score or 0),
        score_breakdown=explanation.get("score_breakdown", {}), matched_skills=explanation.get("matched_skills", []),
        missing_skills=explanation.get("missing_skills", []), partially_matched_areas=explanation.get("partially_matched_areas", []),
        resume_evidence=explanation.get("resume_evidence", {}), ats=explanation.get("ats", {}),
        skill_gaps=[SkillGap.model_validate(item) for item in explanation.get("skill_gaps", [])], created_at=result.created_at,
    )


@router.post("/match", response_model=MatchAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_match_analysis(payload: AnalysisRequest, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> MatchAnalysisResponse:
    repository = CareerRepository(session)
    resume = repository.get_resume(payload.resume_id)
    job = repository.get_job(payload.job_id)
    if resume is None or job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume or job description was not found.")
    assert_record_access(resume.user_id, current_user)
    assert_record_access(job.user_id, current_user)
    explanation = analyze_resume_job(resume.parsed_data or {}, job.parsed_data or {}, resume.extracted_text or "")
    result = session.scalar(
        select(MatchResult).where(MatchResult.resume_id == resume.id, MatchResult.job_id == job.id, MatchResult.analysis_version == 1)
    )
    if result is None:
        result = MatchResult(resume_id=resume.id, job_id=job.id, analysis_version=1)
        session.add(result)
    result.match_score = Decimal(str(explanation["match_score"]))
    result.status = "completed"
    result.explanation = explanation
    session.commit()
    session.refresh(result)
    return _as_response(result)


@router.get("/{analysis_id}", response_model=MatchAnalysisResponse)
def get_match_analysis(analysis_id: UUID, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> MatchAnalysisResponse:
    result = session.get(MatchResult, analysis_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    assert_record_access(result.resume.user_id, current_user)
    return _as_response(result)
