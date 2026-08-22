from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.api.v1.routes.applications import _as_response
from app.db.session import get_db_session
from app.models import InterviewSession, Job, JobApplication, Resume, User
from app.schemas.applications import DashboardResponse

router = APIRouter(prefix="/dashboard")


@router.get("", response_model=DashboardResponse)
def get_dashboard(session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DashboardResponse:
    applications = session.scalars(select(JobApplication).where(JobApplication.user_id == current_user.id).order_by(JobApplication.updated_at.desc())).all()
    counts: dict[str, int] = {}
    for application in applications:
        counts[application.status] = counts.get(application.status, 0) + 1
    return DashboardResponse(
        resume_count=int(session.scalar(select(func.count()).select_from(Resume).where(Resume.user_id == current_user.id)) or 0),
        job_count=int(session.scalar(select(func.count()).select_from(Job).where(Job.user_id == current_user.id)) or 0),
        application_count=len(applications), applications_by_status=counts,
        interviews_in_progress=int(session.scalar(select(func.count()).select_from(InterviewSession).where(InterviewSession.user_id == current_user.id, InterviewSession.status == "in_progress")) or 0),
        recent_applications=[_as_response(application) for application in applications[:5]],
    )
