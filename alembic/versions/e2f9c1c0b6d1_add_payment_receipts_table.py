"""add payment receipts table

Revision ID: e2f9c1c0b6d1
Revises: df1f61be6bfd
Create Date: 2025-07-02 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2f9c1c0b6d1"
down_revision: Union[str, None] = "df1f61be6bfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payment_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receipt_number", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="NGN"),
        sa.Column("payment_date", sa.DateTime(), nullable=False),
        sa.Column("line_items", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_receipts_id"), "payment_receipts", ["id"], unique=False)
    op.create_index(op.f("ix_payment_receipts_receipt_number"), "payment_receipts", ["receipt_number"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_receipts_receipt_number"), table_name="payment_receipts")
    op.drop_index(op.f("ix_payment_receipts_id"), table_name="payment_receipts")
    op.drop_table("payment_receipts")
