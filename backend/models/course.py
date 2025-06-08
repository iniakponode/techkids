from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float, Text
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    age_group = Column(String(100), nullable=False)
    duration = Column(String(100), nullable=False)
    preview_link = Column(String(255), nullable=True)
    rating = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # We specifically do NOT want to auto-delete registrations for the course
    # => remove cascade / ondelete='CASCADE'
    registrations = relationship("Registration", back_populates="course", passive_deletes=True)

    def __repr__(self):
        return (f"<Course(id={self.id}, title={self.title}, price={self.price}, "
                f"duration={self.duration}, age_group={self.age_group})>")