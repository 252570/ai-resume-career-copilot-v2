"""Persistence tests for important Phase 2 relationships and integrity constraints."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Job, JobSkill, MatchResult, Resume, ResumeSkill, Skill, User


def test_career_relationships_persist(db_session: Session) -> None:
    user = User(email="candidate@example.com", display_name="Candidate")
    skill = Skill(canonical_name="Python", category="Programming language")
    resume = Resume(user=user, title="Backend Resume")
    job = Job(user=user, title="Backend Engineer", description="Build reliable services.")
    resume_skill = ResumeSkill(resume=resume, skill=skill, proficiency_level=5, years_experience=Decimal("3.5"))
    job_skill = JobSkill(job=job, skill=skill, importance_level=5, is_required=True)
    result = MatchResult(resume=resume, job=job, match_score=Decimal("82.50"), explanation={"status": "deferred"})

    db_session.add_all([user, skill, resume, job, resume_skill, job_skill, result])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(result)

    assert user.resumes[0].title == "Backend Resume"
    assert user.jobs[0].skills[0].skill.canonical_name == "Python"
    assert user.resumes[0].skills[0].years_experience == Decimal("3.5")
    assert result.explanation == {"status": "deferred"}


def test_user_email_remains_unique(db_session: Session) -> None:
    db_session.add(User(email="unique@example.com", display_name="First Candidate"))
    db_session.commit()
    db_session.add(User(email="unique@example.com", display_name="Second Candidate"))

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
