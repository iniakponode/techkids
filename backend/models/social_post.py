from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.core.database import Base


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)
    image_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    preview_title = Column(String(120), nullable=True)
    preview_description = Column(Text, nullable=True)
    preview_image_url = Column(String(255), nullable=True)
    attempt_count = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    dispatch_logs = relationship(
        "SocialPostDispatchLog",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SocialPlatformCredential(Base):
    __tablename__ = "social_platform_credentials"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, unique=True)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SocialPostDispatchLog(Base):
    __tablename__ = "social_post_dispatch_logs"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer,
        ForeignKey("social_media_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, nullable=False, default=False)
    platform_post_id = Column(String(100), nullable=True)
    diagnostics = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    shares = Column(Integer, nullable=False, default=0)

    post = relationship("SocialMediaPost", back_populates="dispatch_logs")
