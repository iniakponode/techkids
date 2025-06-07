from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.core.database import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())