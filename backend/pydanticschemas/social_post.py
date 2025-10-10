from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class SocialMediaPostBase(BaseModel):
    platform: str = Field(..., max_length=50)
    content: str
    content_type: str
    image_url: str | None = None
    video_url: str | None = None
    scheduled_at: datetime | None = None
    status: str = "draft"


class SocialMediaPostCreate(SocialMediaPostBase):
    preview_title: str | None = None
    preview_description: str | None = None
    preview_image_url: str | None = None


class SocialPostDispatchLogSchema(BaseModel):
    id: int
    attempted_at: datetime
    success: bool
    platform_post_id: str | None = None
    diagnostics: str | None = None
    error_message: str | None = None
    impressions: int
    clicks: int
    comments: int
    shares: int

    class Config:
        from_attributes = True


class SocialPostPreview(BaseModel):
    title: str
    description: str
    thumbnail_url: str | None = None
    platform: str
    content_type: str


class SocialMediaPostSchema(SocialMediaPostBase):
    id: int
    created_at: datetime
    preview_title: str | None = None
    preview_description: str | None = None
    preview_image_url: str | None = None
    attempt_count: int
    last_attempt_at: datetime | None = None
    posted_at: datetime | None = None
    last_error: str | None = None

    class Config:
        from_attributes = True


class SocialMediaPostAnalytics(BaseModel):
    post_id: int
    status: str
    attempt_count: int
    last_attempt_at: datetime | None = None
    posted_at: datetime | None = None
    last_error: str | None = None
    totals: dict[str, int]
    logs: List[SocialPostDispatchLogSchema]


class SocialPlatformCredentialBase(BaseModel):
    platform: str = Field(..., max_length=50)
    access_token: str
    refresh_token: str | None = None
    metadata: str | None = None


class SocialPlatformCredentialCreate(SocialPlatformCredentialBase):
    pass


class SocialPlatformCredentialSchema(SocialPlatformCredentialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
