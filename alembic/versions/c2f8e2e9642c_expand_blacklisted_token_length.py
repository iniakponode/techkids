"""expand blacklisted token length"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c2f8e2e9642c"
down_revision = "1f2741139c4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("blacklisted_tokens", schema=None) as batch_op:
        batch_op.alter_column(
            "token",
            existing_type=sa.String(length=100),
            type_=sa.String(length=512),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("blacklisted_tokens", schema=None) as batch_op:
        batch_op.alter_column(
            "token",
            existing_type=sa.String(length=512),
            type_=sa.String(length=100),
            existing_nullable=True,
        )
