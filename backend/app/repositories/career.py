"""Small persistence operations with transaction ownership left to the calling service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, Resume, Skill, User


class CareerRepository:
    """Database access methods used by future career-domain services."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_resume(self, resume_id: UUID) -> Resume | None:
        return self.session.get(Resume, resume_id)

    def add_resume(self, resume: Resume) -> Resume:
        """Stage a new resume record; callers own commit and rollback boundaries."""
        self.session.add(resume)
        return resume

    def get_job(self, job_id: UUID) -> Job | None:
        return self.session.get(Job, job_id)

    def get_skill_by_name(self, canonical_name: str) -> Skill | None:
        return self.session.scalar(select(Skill).where(Skill.canonical_name == canonical_name))
