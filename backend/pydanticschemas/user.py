from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# Base Schema for User (shared fields)
class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str]=str


# Schema for Creating a User
class UserCreate(UserBase):
    password: str


# Schema for Returning User Data
class UserResponse(UserBase):
    id: int
    role: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
