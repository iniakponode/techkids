from datetime import datetime
from pydantic import BaseModel, Field

class SocialMediaPostBase(BaseModel):
    platform: str = Field(..., max_length=50)
    content: str
    scheduled_at: datetime | None = None
    status: str = "draft"

class SocialMediaPostCreate(SocialMediaPostBase):
    pass

class SocialMediaPostSchema(SocialMediaPostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

