from __future__ import annotations

import hashlib
from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import assert_record_access, get_optional_current_user
from app.core.config import get_settings
from app.core.errors import ResumeUploadError
from app.db.session import get_db_session
from app.models import Job, JobSkill, User
from app.repositories.career import CareerRepository
from app.schemas.job import JobCreateRequest, JobRequirementData, JobResponse
from app.services.job_parser import parse_job_description
from app.services.resume_parser import extract_resume_text, validate_and_detect

router = APIRouter(prefix="/jobs")


def _as_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id, title=job.title, company_name=job.company_name, description=job.description,
        source_url=job.source_url, status=job.status, parsed=JobRequirementData.model_validate(job.parsed_data or {}), created_at=job.created_at,
    )


def _persist_job(payload: JobCreateRequest, session: Session, current_user: User | None) -> JobResponse:
    if current_user is not None:
        if payload.user_id is not None and payload.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A job description can only be added to the authenticated account.")
        payload = payload.model_copy(update={"user_id": current_user.id})
    elif payload.user_id is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required to add a job description to an account.")
    parsed = parse_job_description(payload.description, payload.title, payload.company_name)
    job = Job(
        user_id=payload.user_id,
        title=parsed.job_title or "Untitled job description",
        company_name=parsed.company_name,
        description=payload.description,
        source_url=str(payload.source_url) if payload.source_url else None,
        checksum_sha256=hashlib.sha256(payload.description.encode()).hexdigest(),
        parsed_data=parsed.model_dump(mode="json"), status="parsed",
    )
    repository = CareerRepository(session)
    try:
        repository.add_job(job)
        session.flush()
        required = set(parsed.required_skills)
        for skill_name in parsed.important_keywords:
            skill = repository.get_or_create_skill(skill_name)
            job.skills.append(JobSkill(skill=skill, is_required=skill_name in required, importance_level=5 if skill_name in required else 3, evidence=skill_name))
        session.commit()
        session.refresh(job)
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="The job description could not be saved.") from exc
    return _as_response(job)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreateRequest, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> JobResponse:
    return _persist_job(payload, session, current_user)


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_job_description(
    file: UploadFile = File(...), user_id: UUID | None = Form(default=None), title: str | None = Form(default=None), company_name: str | None = Form(default=None), session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)
) -> JobResponse:
    content = await file.read(get_settings().max_resume_upload_bytes + 1)
    await file.close()
    if len(content) > get_settings().max_resume_upload_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Job description files must not exceed 5 MB.")
    try:
        suffix, _ = validate_and_detect(file.filename, content)
        description = extract_resume_text(content, suffix)
    except ResumeUploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    default_title = title or PurePath(file.filename or "job description").stem
    return _persist_job(JobCreateRequest(description=description, title=default_title, company_name=company_name, user_id=user_id), session, current_user)


@router.get("", response_model=list[JobResponse])
def list_jobs(user_id: UUID | None = None, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> list[JobResponse]:
    if current_user is not None:
        if user_id is not None and user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Job lists can only be requested for the authenticated account.")
        user_id = current_user.id
    elif user_id is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required to list account jobs.")
    return [_as_response(job) for job in CareerRepository(session).list_jobs(user_id)]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, session: Session = Depends(get_db_session), current_user: User | None = Depends(get_optional_current_user)) -> JobResponse:
    job = CareerRepository(session).get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
    assert_record_access(job.user_id, current_user)
    return _as_response(job)
