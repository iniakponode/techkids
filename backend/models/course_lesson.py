"""Database model describing an individual lesson within a module."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.database import Base


class CourseLesson(Base):
    """Represents a lesson nested under a course module."""

    __tablename__ = "course_lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(
        Integer,
        ForeignKey("course_modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    duration_minutes = Column(Integer, nullable=True)
    resource_url = Column(String(255), nullable=True)

    module = relationship("CourseModule", back_populates="lessons")
    lesson_progress_entries = relationship(
        "LessonProgress",
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<CourseLesson(id={self.id}, module_id={self.module_id}, title={self.title!r})>"
