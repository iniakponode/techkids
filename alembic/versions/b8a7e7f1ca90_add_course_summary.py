"""add course summary field

Revision ID: b8a7e7f1ca90
Revises: df1f61be6bfd
Create Date: 2025-07-10 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8a7e7f1ca90'
down_revision: Union[str, None] = 'df1f61be6bfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('courses', sa.Column('summary', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('courses', 'summary')
