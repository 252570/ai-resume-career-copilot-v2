"""Add minimal persisted parsing fields to existing resume metadata.

Revision ID: 20260822_0002
Revises: 20260820_0001
Create Date: 2026-08-22 10:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260822_0002"
down_revision: Union[str, Sequence[str], None] = "20260820_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("resumes", "user_id", existing_type=sa.Uuid(), nullable=True)
    op.add_column("resumes", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("resumes", sa.Column("parsed_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("resumes", "parsed_data")
    op.drop_column("resumes", "extracted_text")
    op.alter_column("resumes", "user_id", existing_type=sa.Uuid(), nullable=False)
