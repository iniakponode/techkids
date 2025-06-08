"""add course category field

Revision ID: df1f61be6bfd
Revises: 0b8d63f18eb1
Create Date: 2025-06-18 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'df1f61be6bfd'
down_revision: Union[str, None] = '0b8d63f18eb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('courses', sa.Column('category', sa.String(length=100), nullable=True))

def downgrade() -> None:
    op.drop_column('courses', 'category')
