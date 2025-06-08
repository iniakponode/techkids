from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TestimonialBase(BaseModel):
    name: str = Field(..., max_length=100)
    content: str

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_approved: Optional[bool] = None

class TestimonialSchema(TestimonialBase):
    id: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
