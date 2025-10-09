"""Database model storing per-lesson completion state for a registration."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.core.database import Base


class LessonProgress(Base):
    """Tracks a learner's status for a specific lesson."""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("progress_id", "lesson_id", name="uq_lesson_progress_progress_lesson"),
    )

    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(
        Integer,
        ForeignKey("learning_progress.id", ondelete="CASCADE"),
        nullable=False,
    )
    lesson_id = Column(
        Integer,
        ForeignKey("course_lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(20), nullable=False, default="not_started")
    completed_at = Column(DateTime, nullable=True)

    progress = relationship("LearningProgress", back_populates="lesson_progress")
    lesson = relationship("CourseLesson", back_populates="lesson_progress_entries")

    def __repr__(self) -> str:  # pragma: no cover - debugging convenience
        return (
            "<LessonProgress(progress_id={progress}, lesson_id={lesson}, "
            "status={status})>".format(
                progress=self.progress_id,
                lesson=self.lesson_id,
                status=self.status,
            )
        )
