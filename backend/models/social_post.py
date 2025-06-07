from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.core.database import Base

class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

