from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
