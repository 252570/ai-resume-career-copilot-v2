"""add interview practice

Revision ID: 20260822_0006
Revises: 20260822_0005
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260822_0006"
down_revision = "20260822_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("interview_sessions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("resume_id", sa.Uuid(), sa.ForeignKey("resumes.id", ondelete="SET NULL")), sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="SET NULL")), sa.Column("title", sa.String(255), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("questions", postgresql.JSONB(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_interview_sessions_user_created", "interview_sessions", ["user_id", "created_at"])
    op.create_table("interview_responses", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("session_id", sa.Uuid(), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False), sa.Column("question_index", sa.Integer(), nullable=False), sa.Column("answer", sa.Text(), nullable=False), sa.Column("heuristic_score", sa.Integer(), nullable=False), sa.Column("feedback", postgresql.JSONB(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("session_id", "question_index", name="uq_interview_responses_session_question"))


def downgrade() -> None:
    op.drop_table("interview_responses")
    op.drop_table("interview_sessions")
