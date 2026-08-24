"""add parsed job requirement data

Revision ID: 20260822_0003
Revises: 20260822_0002
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260822_0003"
down_revision = "20260822_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("status", sa.String(length=32), server_default="parsed", nullable=False))
    op.add_column("jobs", sa.Column("parsed_data", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "parsed_data")
    op.drop_column("jobs", "status")
