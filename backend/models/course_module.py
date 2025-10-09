"""Database model describing a structured module within a course."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.database import Base


class CourseModule(Base):
    """Represents a logical module within a course syllabus."""

    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)

    course = relationship("Course", back_populates="modules")
    lessons = relationship(
        "CourseLesson",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="CourseLesson.position",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<CourseModule(id={self.id}, course_id={self.course_id}, title={self.title!r})>"
