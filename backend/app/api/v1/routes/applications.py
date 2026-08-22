from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import assert_record_access, get_current_user
from app.db.session import get_db_session
from app.models import JobApplication, User
from app.repositories.career import CareerRepository
from app.schemas.applications import JobApplicationCreateRequest, JobApplicationResponse, JobApplicationUpdateRequest

router = APIRouter(prefix="/applications")


def _as_response(record: JobApplication) -> JobApplicationResponse:
    return JobApplicationResponse(id=record.id, job_id=record.job_id, company_name=record.company_name, role_title=record.role_title, status=record.status, applied_at=record.applied_at, next_step_at=record.next_step_at, notes=record.notes, created_at=record.created_at, updated_at=record.updated_at)


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(payload: JobApplicationCreateRequest, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> JobApplicationResponse:
    if payload.job_id:
        job = CareerRepository(session).get_job(payload.job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
        assert_record_access(job.user_id, current_user)
    applied_at = payload.applied_at or (datetime.now(timezone.utc) if payload.status == "applied" else None)
    record = JobApplication(user_id=current_user.id, **payload.model_dump(exclude={"applied_at"}), applied_at=applied_at)
    session.add(record)
    session.commit()
    session.refresh(record)
    return _as_response(record)


@router.get("", response_model=list[JobApplicationResponse])
def list_applications(session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> list[JobApplicationResponse]:
    records = session.scalars(select(JobApplication).where(JobApplication.user_id == current_user.id).order_by(JobApplication.updated_at.desc())).all()
    return [_as_response(record) for record in records]


@router.patch("/{application_id}", response_model=JobApplicationResponse)
def update_application(application_id: UUID, payload: JobApplicationUpdateRequest, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> JobApplicationResponse:
    record = session.get(JobApplication, application_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    values = payload.model_dump(exclude_unset=True)
    for field, value in values.items():
        setattr(record, field, value)
    if record.status == "applied" and record.applied_at is None:
        record.applied_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(record)
    return _as_response(record)
