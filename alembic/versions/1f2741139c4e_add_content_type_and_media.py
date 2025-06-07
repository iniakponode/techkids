"""add content type and media fields to social media posts

Revision ID: 1f2741139c4e
Revises: 0b8d63f18eb1
Create Date: 2025-06-08 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1f2741139c4e'
down_revision: Union[str, None] = '0b8d63f18eb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('social_media_posts', sa.Column('content_type', sa.String(length=50), nullable=False, server_default='feed'))
    op.add_column('social_media_posts', sa.Column('image_url', sa.String(length=255), nullable=True))
    op.add_column('social_media_posts', sa.Column('video_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('social_media_posts', 'video_url')
    op.drop_column('social_media_posts', 'image_url')
    op.drop_column('social_media_posts', 'content_type')
