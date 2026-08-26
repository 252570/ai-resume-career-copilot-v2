"""add roadmap completion state

Revision ID: 20260826_0008
Revises: 20260822_0007
"""

from alembic import op
import sqlalchemy as sa

revision = "20260826_0008"
down_revision = "20260822_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roadmap_items", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("roadmap_items", "completed_at")
