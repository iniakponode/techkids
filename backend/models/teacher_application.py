from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.core.database import Base

class TeacherApplication(Base):
    __tablename__ = "teacher_applications"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TeacherApplication(id={self.id}, email={self.email})>"
