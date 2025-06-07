from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import List, Optional

# Schema for Creating a Registration
class RegistrationCreate(BaseModel):
    fullName: str
    password: str
    phone: str
    course_id: int
    role: Optional[str] = "student"  # Student, Parent, Teacher, etc.
    
class PublicRegistrationRequest(BaseModel):
    fullName: str
    email: str
    password: str
    confirm_password: str
    phone: str
    course_ids: List[int]
    role: str = "student"

class UserRegistrationRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str
    phone: str
    course_ids: List[int]
    role: Optional[str] = "student"
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.confirm_password != self.password:
            raise ValueError("Passwords do not match")
        return self

# Schema for Returning Registration Data
class RegistrationResponse(BaseModel):
    id: int
    fullName: str
    phone: str
    course_ids: List[int]  # a list of course IDs
    registered_at: datetime
    status: str = "pending"
    is_verified: bool = False

    class Config:
        from_attributes = True
