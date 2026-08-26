from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.config import get_settings
from app.db.session import get_db_session
from app.models import InterviewSession, Job, JobApplication, MatchResult, Resume, User
from app.services.resume_storage import ResumeStorage

router = APIRouter(prefix="/account")


def _value(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def _resume_export(resume: Resume) -> dict[str, object]:
    return {
        "id": _value(resume.id),
        "title": resume.title,
        "original_filename": resume.original_filename,
        "content_type": resume.content_type,
        "byte_size": resume.byte_size,
        "status": resume.status,
        "parsed_data": resume.parsed_data or {},
        "created_at": _value(resume.created_at),
        "updated_at": _value(resume.updated_at),
    }


def _job_export(job: Job) -> dict[str, object]:
    return {
        "id": _value(job.id),
        "title": job.title,
        "company_name": job.company_name,
        "description": job.description,
        "source_url": job.source_url,
        "location": job.location,
        "employment_type": job.employment_type,
        "status": job.status,
        "parsed_data": job.parsed_data or {},
        "created_at": _value(job.created_at),
        "updated_at": _value(job.updated_at),
    }


@router.get("/export")
def export_account(user: User = Depends(get_current_user), session: Session = Depends(get_db_session)) -> dict[str, object]:
    """Return the authenticated user's career records as a portable JSON document."""
    resumes = session.query(Resume).filter(Resume.user_id == user.id).all()
    jobs = session.query(Job).filter(Job.user_id == user.id).all()
    analyses = session.query(MatchResult).join(Resume).filter(Resume.user_id == user.id).all()
    applications = session.query(JobApplication).filter(JobApplication.user_id == user.id).all()
    interviews = session.query(InterviewSession).filter(InterviewSession.user_id == user.id).all()

    return {
        "export_version": 1,
        "exported_at": datetime.now().astimezone().isoformat(),
        "profile": {"id": _value(user.id), "email": user.email, "display_name": user.display_name, "profile_headline": user.profile_headline},
        "resumes": [_resume_export(resume) for resume in resumes],
        "jobs": [_job_export(job) for job in jobs],
        "analyses": [
            {
                "id": _value(analysis.id),
                "resume_id": _value(analysis.resume_id),
                "job_id": _value(analysis.job_id),
                "analysis_version": analysis.analysis_version,
                "match_score": float(analysis.match_score) if analysis.match_score is not None else None,
                "status": analysis.status,
                "explanation": analysis.explanation or {},
                "roadmap": [
                    {"skill": item.skill, "priority": item.priority, "sequence": item.sequence, "practice_suggestion": item.practice_suggestion, "learning_stage": item.learning_stage}
                    for item in analysis.roadmap_items
                ],
                "projects": [
                    {"title": item.title, "purpose": item.purpose, "skills_developed": item.skills_developed, "suggested_technology": item.suggested_technology, "difficulty": item.difficulty, "portfolio_value": item.portfolio_value}
                    for item in analysis.project_recommendations
                ],
                "created_at": _value(analysis.created_at),
            }
            for analysis in analyses
        ],
        "applications": [
            {
                "id": _value(item.id),
                "job_id": _value(item.job_id),
                "company_name": item.company_name,
                "role_title": item.role_title,
                "status": item.status,
                "applied_at": _value(item.applied_at),
                "next_step_at": _value(item.next_step_at),
                "notes": item.notes,
                "created_at": _value(item.created_at),
            }
            for item in applications
        ],
        "interviews": [
            {
                "id": _value(item.id),
                "resume_id": _value(item.resume_id),
                "job_id": _value(item.job_id),
                "title": item.title,
                "status": item.status,
                "questions": item.questions,
                "responses": [
                    {
                        "question_index": response.question_index,
                        "answer": response.answer,
                        "heuristic_score": response.heuristic_score,
                        "feedback": response.feedback,
                    }
                    for response in item.responses
                ],
                "created_at": _value(item.created_at),
            }
            for item in interviews
        ],
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(user: User = Depends(get_current_user), session: Session = Depends(get_db_session)) -> Response:
    """Permanently remove the authenticated account and its owned career records."""
    settings = get_settings()
    storage = ResumeStorage(settings.resume_storage_dir)
    resumes = session.query(Resume).filter(Resume.user_id == user.id).all()
    for resume in resumes:
        if resume.storage_key:
            storage.delete(resume.storage_key)

    # Jobs use SET NULL for other references, so delete the user's jobs explicitly
    # before deleting the user to avoid leaving their private descriptions orphaned.
    session.query(Job).filter(Job.user_id == user.id).delete(synchronize_session=False)
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
