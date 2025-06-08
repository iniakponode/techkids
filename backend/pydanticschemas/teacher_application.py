from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherApplicationCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None
