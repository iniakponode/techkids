"""add social media post schedule

Revision ID: 0b8d63f18eb1
Revises: d3e7e614a003
Create Date: 2025-06-08 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0b8d63f18eb1'
down_revision: Union[str, None] = 'd3e7e614a003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'social_media_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_media_posts_id'), 'social_media_posts', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_social_media_posts_id'), table_name='social_media_posts')
    op.drop_table('social_media_posts')
