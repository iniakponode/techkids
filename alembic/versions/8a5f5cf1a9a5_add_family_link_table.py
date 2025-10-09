"""add family link table

Revision ID: 8a5f5cf1a9a5
Revises: 4f81d3a6c9c9
Create Date: 2025-10-09 03:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a5f5cf1a9a5"
down_revision = "4f81d3a6c9c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("relationship_label", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "parent_id",
            "child_id",
            name="uq_family_link_parent_child",
        ),
    )


def downgrade() -> None:
    op.drop_table("family_links")
