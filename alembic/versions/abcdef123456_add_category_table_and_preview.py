"""add category table and preview link"""

revision = 'abcdef123456'
down_revision = 'df1f61be6bfd'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.add_column('courses', sa.Column('preview_link', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('courses', 'preview_link')
    op.drop_table('categories')
