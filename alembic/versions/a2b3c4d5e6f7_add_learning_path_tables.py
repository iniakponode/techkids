"""Add course module, lesson, and lesson progress tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2b3c4d5e6f7"
down_revision = "8a5f5cf1a9a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_modules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_course_modules_id"),
        "course_modules",
        ["id"],
        unique=False,
    )

    op.create_table(
        "course_lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("resource_url", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["module_id"], ["course_modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_course_lessons_id"),
        "course_lessons",
        ["id"],
        unique=False,
    )

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("progress_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["progress_id"], ["learning_progress.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["course_lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "progress_id",
            "lesson_id",
            name="uq_lesson_progress_progress_lesson",
        ),
    )
    op.create_index(
        op.f("ix_lesson_progress_id"),
        "lesson_progress",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_lesson_progress_id"), table_name="lesson_progress")
    op.drop_table("lesson_progress")
    op.drop_index(op.f("ix_course_lessons_id"), table_name="course_lessons")
    op.drop_table("course_lessons")
    op.drop_index(op.f("ix_course_modules_id"), table_name="course_modules")
    op.drop_table("course_modules")
