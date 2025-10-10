"""Enhance social media automation with analytics tables

Revision ID: e5c6f2b4d8aa
Revises: 1f2741139c4e_add_content_type_and_media
Create Date: 2024-05-26 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e5c6f2b4d8aa"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "social_media_posts",
        sa.Column("preview_title", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "social_media_posts",
        sa.Column("preview_description", sa.Text(), nullable=True),
    )
    op.add_column(
        "social_media_posts",
        sa.Column("preview_image_url", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "social_media_posts",
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "social_media_posts",
        sa.Column("last_attempt_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "social_media_posts",
        sa.Column("posted_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "social_media_posts",
        sa.Column("last_error", sa.Text(), nullable=True),
    )

    op.create_table(
        "social_platform_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("access_token", sa.String(length=255), nullable=False),
        sa.Column("refresh_token", sa.String(length=255), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform"),
    )

    op.create_table(
        "social_post_dispatch_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("platform_post_id", sa.String(length=100), nullable=True),
        sa.Column("diagnostics", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["post_id"], ["social_media_posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_social_post_dispatch_logs_post_id"),
        "social_post_dispatch_logs",
        ["post_id"],
    )

    op.create_index(
        op.f("ix_social_platform_credentials_id"),
        "social_platform_credentials",
        ["id"],
    )
    op.create_index(
        op.f("ix_social_media_posts_attempt_count"),
        "social_media_posts",
        ["attempt_count"],
    )
    op.alter_column(
        "social_media_posts",
        "attempt_count",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_social_media_posts_attempt_count"), table_name="social_media_posts")
    op.drop_index(op.f("ix_social_platform_credentials_id"), table_name="social_platform_credentials")
    op.drop_index(op.f("ix_social_post_dispatch_logs_post_id"), table_name="social_post_dispatch_logs")
    op.drop_table("social_post_dispatch_logs")
    op.drop_table("social_platform_credentials")
    op.drop_column("social_media_posts", "last_error")
    op.drop_column("social_media_posts", "posted_at")
    op.drop_column("social_media_posts", "last_attempt_at")
    op.drop_column("social_media_posts", "attempt_count")
    op.drop_column("social_media_posts", "preview_image_url")
    op.drop_column("social_media_posts", "preview_description")
    op.drop_column("social_media_posts", "preview_title")
