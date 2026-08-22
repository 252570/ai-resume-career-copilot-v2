"""Phase 3 multipart resume upload and metadata retrieval endpoints."""

from __future__ import annotations

import hashlib
import logging
from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ResumeUploadError
from app.db.session import get_db_session
from app.models import Resume, User
from app.repositories.career import CareerRepository
from app.schemas.resume import ParsedResumeData, ResumeDetailResponse, ResumeUploadResponse
from app.services.resume_parser import extract_resume_text, parse_resume_text, validate_and_detect
from app.services.resume_storage import ResumeStorage

router = APIRouter(prefix="/resumes")
logger = logging.getLogger(__name__)


def get_resume_storage() -> ResumeStorage:
    """Provide local-development upload storage through runtime configuration."""
    return ResumeStorage(get_settings().resume_storage_dir)


def _as_response(resume: Resume) -> ResumeDetailResponse:
    parsed = ParsedResumeData.model_validate(resume.parsed_data or {})
    return ResumeDetailResponse(
        id=resume.id,
        filename=resume.original_filename or resume.title,
        content_type=resume.content_type or "application/octet-stream",
        file_size=resume.byte_size or 0,
        status=resume.status,
        parsed=parsed,
        uploaded_at=resume.created_at,
    )


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: UUID | None = Form(default=None),
    session: Session = Depends(get_db_session),
    storage: ResumeStorage = Depends(get_resume_storage),
) -> ResumeUploadResponse:
    """Validate, store, deterministically parse, and persist an uploaded resume."""
    settings = get_settings()
    try:
        content = await file.read(settings.max_resume_upload_bytes + 1)
    finally:
        await file.close()

    if len(content) > settings.max_resume_upload_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Resume files must not exceed 5 MB.")

    try:
        suffix, detected_type = validate_and_detect(file.filename, content)
        extracted_text = extract_resume_text(content, suffix)
        parsed = parse_resume_text(extracted_text)
    except ResumeUploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    if user_id is not None and session.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The supplied user was not found.")

    stored_file = storage.save(content, suffix)
    original_filename = PurePath(file.filename or f"resume{suffix}").name[:255]
    resume = Resume(
        user_id=user_id,
        title=PurePath(original_filename).stem[:160] or "Uploaded resume",
        original_filename=original_filename,
        storage_key=stored_file.storage_key,
        content_type=detected_type,
        byte_size=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        extracted_text=extracted_text,
        parsed_data=parsed.model_dump(mode="json"),
        status="parsed",
    )
    try:
        CareerRepository(session).add_resume(resume)
        session.commit()
        session.refresh(resume)
    except SQLAlchemyError as exc:
        session.rollback()
        storage.delete(stored_file.storage_key)
        logger.exception("Resume metadata persistence failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="The resume could not be saved.") from exc

    response = _as_response(resume)
    return ResumeUploadResponse(**response.model_dump())


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: UUID, session: Session = Depends(get_db_session)) -> ResumeDetailResponse:
    """Return stored metadata and parsed fields without exposing local filesystem paths or file bytes."""
    resume = CareerRepository(session).get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return _as_response(resume)
