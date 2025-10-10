"""add learning progress table

Revision ID: 4f81d3a6c9c9
Revises: d3e7e614a003
Create Date: 2025-10-09 02:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f81d3a6c9c9"
down_revision = "d3e7e614a003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column(
            "completed_lessons",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "total_lessons",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "completion_percentage",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("current_module", sa.String(length=255), nullable=True),
        sa.Column("current_lesson", sa.String(length=255), nullable=True),
        sa.Column(
            "last_activity_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["registration_id"], ["registrations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_id"),
    )


def downgrade() -> None:
    op.drop_table("learning_progress")
