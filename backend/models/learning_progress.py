"""Database model for tracking learner progress within a course."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.core.database import Base


class LearningProgress(Base):
    """Represents aggregated progress for a single course registration."""

    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(
        Integer,
        ForeignKey("registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    completed_lessons = Column(Integer, default=0, nullable=False)
    total_lessons = Column(Integer, default=0, nullable=False)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    current_module = Column(String(255), nullable=True)
    current_lesson = Column(String(255), nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    registration = relationship(
        "Registration", back_populates="progress", passive_deletes=True
    )
    lesson_progress = relationship(
        "LessonProgress",
        back_populates="progress",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging convenience
        return (
            "<LearningProgress(registration_id={reg}, completion={pct:.1f}%, "
            "completed_lessons={done}, total_lessons={total})>".format(
                reg=self.registration_id,
                pct=self.completion_percentage,
                done=self.completed_lessons,
                total=self.total_lessons,
            )
        )
