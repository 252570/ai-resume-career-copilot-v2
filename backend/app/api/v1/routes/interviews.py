from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import assert_record_access, get_current_user
from app.db.session import get_db_session
from app.models import InterviewResponse, InterviewSession, User
from app.repositories.career import CareerRepository
from app.schemas.interviews import InterviewAnswerFeedback, InterviewResponseCreateRequest, InterviewResponseDetail, InterviewSessionCreateRequest, InterviewSessionResponse
from app.services.interviews import evaluate_answer, generate_questions

router = APIRouter(prefix="/interviews")


def _as_response(session_record: InterviewSession) -> InterviewSessionResponse:
    return InterviewSessionResponse(id=session_record.id, title=session_record.title, status=session_record.status, questions=session_record.questions, responses=[InterviewResponseDetail(question_index=item.question_index, answer=item.answer, feedback=InterviewAnswerFeedback.model_validate(item.feedback)) for item in sorted(session_record.responses, key=lambda item: item.question_index)], created_at=session_record.created_at)


@router.post("", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_interview_session(payload: InterviewSessionCreateRequest, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> InterviewSessionResponse:
    repository = CareerRepository(session)
    resume = repository.get_resume(payload.resume_id) if payload.resume_id else None
    job = repository.get_job(payload.job_id) if payload.job_id else None
    if payload.resume_id and resume is None or payload.job_id and job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The selected resume or job description was not found.")
    if resume:
        assert_record_access(resume.user_id, current_user)
    if job:
        assert_record_access(job.user_id, current_user)
    questions = generate_questions(job.parsed_data if job else {}, payload.question_count)
    record = InterviewSession(user_id=current_user.id, resume_id=resume.id if resume else None, job_id=job.id if job else None, title=f"Practice: {job.title if job else 'general interview'}", questions=questions)
    session.add(record)
    session.commit()
    session.refresh(record)
    return _as_response(record)


@router.get("", response_model=list[InterviewSessionResponse])
def list_interview_sessions(session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> list[InterviewSessionResponse]:
    records = session.scalars(select(InterviewSession).where(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc())).all()
    return [_as_response(record) for record in records]


@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_interview_session(session_id: UUID, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> InterviewSessionResponse:
    record = session.get(InterviewSession, session_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview practice session not found.")
    return _as_response(record)


@router.post("/{session_id}/responses", response_model=InterviewSessionResponse)
def save_interview_response(session_id: UUID, payload: InterviewResponseCreateRequest, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> InterviewSessionResponse:
    record = session.get(InterviewSession, session_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview practice session not found.")
    if payload.question_index >= len(record.questions):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Question index is outside this practice session.")
    question = record.questions[payload.question_index]
    feedback = evaluate_answer(payload.answer, question.get("focus_skill"))
    answer = session.scalar(select(InterviewResponse).where(InterviewResponse.session_id == record.id, InterviewResponse.question_index == payload.question_index))
    if answer is None:
        answer = InterviewResponse(session_id=record.id, question_index=payload.question_index, answer=payload.answer, heuristic_score=int(feedback["score"]), feedback=feedback)
        session.add(answer)
    else:
        answer.answer, answer.heuristic_score, answer.feedback = payload.answer, int(feedback["score"]), feedback
    if len(record.responses) + (1 if answer.id is None else 0) >= len(record.questions):
        record.status = "completed"
    session.commit()
    session.refresh(record)
    return _as_response(record)
