from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
