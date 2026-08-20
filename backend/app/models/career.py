"""Normalized career-domain ORM models; no scoring or AI behavior belongs in this layer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    """Consistent UTC-oriented creation and update metadata."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    profile_headline: Mapped[str | None] = mapped_column(String(255))

    resumes: Mapped[list[Resume]] = relationship(back_populates="user", cascade="all, delete-orphan")
    jobs: Mapped[list[Job]] = relationship(back_populates="user")


class Resume(TimestampMixin, Base):
    __tablename__ = "resumes"
    __table_args__ = (
        Index("ix_resumes_user_created_at", "user_id", "created_at"),
        Index("ix_resumes_user_title", "user_id", "title"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    storage_key: Mapped[str | None] = mapped_column(String(512), unique=True)
    content_type: Mapped[str | None] = mapped_column(String(127))
    byte_size: Mapped[int | None] = mapped_column(Integer)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), server_default="pending", nullable=False)

    user: Mapped[User] = relationship(back_populates="resumes")
    skills: Mapped[list[ResumeSkill]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    match_results: Mapped[list[MatchResult]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_user_created_at", "user_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    location: Mapped[str | None] = mapped_column(String(255))
    employment_type: Mapped[str | None] = mapped_column(String(64))
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), index=True)

    user: Mapped[User | None] = relationship(back_populates="jobs")
    skills: Mapped[list[JobSkill]] = relationship(back_populates="job", cascade="all, delete-orphan")
    match_results: Mapped[list[MatchResult]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Skill(TimestampMixin, Base):
    __tablename__ = "skills"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    canonical_name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    resumes: Mapped[list[ResumeSkill]] = relationship(back_populates="skill")
    jobs: Mapped[list[JobSkill]] = relationship(back_populates="skill")


class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    __table_args__ = (
        CheckConstraint("proficiency_level BETWEEN 1 AND 5", name="ck_resume_skills_proficiency_level"),
        CheckConstraint("years_experience IS NULL OR years_experience >= 0", name="ck_resume_skills_years_experience"),
        Index("ix_resume_skills_skill_id", "skill_id"),
    )

    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[UUID] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"), primary_key=True)
    proficiency_level: Mapped[int | None] = mapped_column(Integer)
    years_experience: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text)

    resume: Mapped[Resume] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship(back_populates="resumes")


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
        CheckConstraint("importance_level BETWEEN 1 AND 5", name="ck_job_skills_importance_level"),
        Index("ix_job_skills_skill_required", "skill_id", "is_required"),
    )

    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[UUID] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"), primary_key=True)
    importance_level: Mapped[int] = mapped_column(Integer, server_default="3", nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text)

    job: Mapped[Job] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship(back_populates="jobs")


class MatchResult(TimestampMixin, Base):
    __tablename__ = "match_results"
    __table_args__ = (
        CheckConstraint("match_score BETWEEN 0 AND 100", name="ck_match_results_score"),
        UniqueConstraint("resume_id", "job_id", "analysis_version", name="uq_match_results_resume_job_version"),
        Index("ix_match_results_job_created_at", "job_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_version: Mapped[int] = mapped_column(Integer, server_default="1", nullable=False)
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(32), server_default="pending", nullable=False)
    explanation: Mapped[dict[str, object] | None] = mapped_column(JSONB().with_variant(JSON, "sqlite"))

    resume: Mapped[Resume] = relationship(back_populates="match_results")
    job: Mapped[Job] = relationship(back_populates="match_results")
