"""add career plan tables

Revision ID: 20260822_0004
Revises: 20260822_0003
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260822_0004"
down_revision = "20260822_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("roadmap_items", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("match_result_id", sa.Uuid(), sa.ForeignKey("match_results.id", ondelete="CASCADE"), nullable=False), sa.Column("skill", sa.String(160), nullable=False), sa.Column("priority", sa.String(32), nullable=False), sa.Column("prerequisites", postgresql.JSONB(), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("practice_suggestion", sa.Text(), nullable=False), sa.Column("learning_stage", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("match_result_id", "skill", name="uq_roadmap_items_match_skill"))
    op.create_index("ix_roadmap_items_match_sequence", "roadmap_items", ["match_result_id", "sequence"])
    op.create_table("project_recommendations", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("match_result_id", sa.Uuid(), sa.ForeignKey("match_results.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("purpose", sa.Text(), nullable=False), sa.Column("skills_developed", postgresql.JSONB(), nullable=False), sa.Column("suggested_technology", postgresql.JSONB(), nullable=False), sa.Column("difficulty", sa.String(64), nullable=False), sa.Column("portfolio_value", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("match_result_id", "title", name="uq_project_recommendations_match_title"))
    op.create_index("ix_project_recommendations_match_difficulty", "project_recommendations", ["match_result_id", "difficulty"])


def downgrade() -> None:
    op.drop_table("project_recommendations")
    op.drop_table("roadmap_items")
