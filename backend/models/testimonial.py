from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from backend.core.database import Base

class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Testimonial(id={self.id}, name={self.name})>"
