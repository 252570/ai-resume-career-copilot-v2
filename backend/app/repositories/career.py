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

    def list_resumes(self, user_id: UUID | None = None) -> list[Resume]:
        statement = select(Resume).order_by(Resume.created_at.desc())
        if user_id is not None:
            statement = statement.where(Resume.user_id == user_id)
        return list(self.session.scalars(statement))

    def add_resume(self, resume: Resume) -> Resume:
        """Stage a new resume record; callers own commit and rollback boundaries."""
        self.session.add(resume)
        return resume

    def get_job(self, job_id: UUID) -> Job | None:
        return self.session.get(Job, job_id)

    def list_jobs(self, user_id: UUID | None = None) -> list[Job]:
        statement = select(Job).order_by(Job.created_at.desc())
        if user_id is not None:
            statement = statement.where(Job.user_id == user_id)
        return list(self.session.scalars(statement))

    def add_job(self, job: Job) -> Job:
        self.session.add(job)
        return job

    def get_or_create_skill(self, canonical_name: str) -> Skill:
        skill = self.get_skill_by_name(canonical_name)
        if skill is None:
            skill = Skill(canonical_name=canonical_name)
            self.session.add(skill)
            self.session.flush()
        return skill

    def get_skill_by_name(self, canonical_name: str) -> Skill | None:
        return self.session.scalar(select(Skill).where(Skill.canonical_name == canonical_name))
