"""Create the normalized Phase 2 career-domain PostgreSQL schema.

Revision ID: 20260820_0001
Revises:
Create Date: 2026-08-20 14:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260820_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("profile_headline", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("canonical_name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canonical_name"),
    )
    op.create_index("ix_skills_canonical_name", "skills", ["canonical_name"], unique=True)
    op.create_index("ix_skills_category", "skills", ["category"], unique=False)

    op.create_table(
        "resumes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("content_type", sa.String(length=127), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_resumes_checksum_sha256", "resumes", ["checksum_sha256"], unique=False)
    op.create_index("ix_resumes_user_created_at", "resumes", ["user_id", "created_at"], unique=False)
    op.create_index("ix_resumes_user_title", "resumes", ["user_id", "title"], unique=False)

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=64), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_checksum_sha256", "jobs", ["checksum_sha256"], unique=False)
    op.create_index("ix_jobs_company_name", "jobs", ["company_name"], unique=False)
    op.create_index("ix_jobs_user_created_at", "jobs", ["user_id", "created_at"], unique=False)

    op.create_table(
        "resume_skills",
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("proficiency_level", sa.Integer(), nullable=True),
        sa.Column("years_experience", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.CheckConstraint("proficiency_level BETWEEN 1 AND 5", name="ck_resume_skills_proficiency_level"),
        sa.CheckConstraint("years_experience IS NULL OR years_experience >= 0", name="ck_resume_skills_years_experience"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("resume_id", "skill_id"),
    )
    op.create_index("ix_resume_skills_skill_id", "resume_skills", ["skill_id"], unique=False)

    op.create_table(
        "job_skills",
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("importance_level", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.CheckConstraint("importance_level BETWEEN 1 AND 5", name="ck_job_skills_importance_level"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("job_id", "skill_id"),
    )
    op.create_index("ix_job_skills_skill_required", "job_skills", ["skill_id", "is_required"], unique=False)

    op.create_table(
        "match_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("match_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("match_score BETWEEN 0 AND 100", name="ck_match_results_score"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_id", "job_id", "analysis_version", name="uq_match_results_resume_job_version"),
    )
    op.create_index("ix_match_results_job_created_at", "match_results", ["job_id", "created_at"], unique=False)
    op.create_index("ix_match_results_resume_id", "match_results", ["resume_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_match_results_resume_id", table_name="match_results")
    op.drop_index("ix_match_results_job_created_at", table_name="match_results")
    op.drop_table("match_results")
    op.drop_index("ix_job_skills_skill_required", table_name="job_skills")
    op.drop_table("job_skills")
    op.drop_index("ix_resume_skills_skill_id", table_name="resume_skills")
    op.drop_table("resume_skills")
    op.drop_index("ix_jobs_user_created_at", table_name="jobs")
    op.drop_index("ix_jobs_company_name", table_name="jobs")
    op.drop_index("ix_jobs_checksum_sha256", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_resumes_user_title", table_name="resumes")
    op.drop_index("ix_resumes_user_created_at", table_name="resumes")
    op.drop_index("ix_resumes_checksum_sha256", table_name="resumes")
    op.drop_table("resumes")
    op.drop_index("ix_skills_category", table_name="skills")
    op.drop_index("ix_skills_canonical_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
