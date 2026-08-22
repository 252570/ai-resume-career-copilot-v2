"""add job applications

Revision ID: 20260822_0007
Revises: 20260822_0006
"""

from alembic import op
import sqlalchemy as sa

revision = "20260822_0007"
down_revision = "20260822_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("job_applications", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="SET NULL")), sa.Column("company_name", sa.String(255), nullable=False), sa.Column("role_title", sa.String(255), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("applied_at", sa.DateTime(timezone=True)), sa.Column("next_step_at", sa.DateTime(timezone=True)), sa.Column("notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_job_applications_user_status_updated", "job_applications", ["user_id", "status", "updated_at"])


def downgrade() -> None:
    op.drop_table("job_applications")
