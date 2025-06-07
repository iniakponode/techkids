# backend/pydanticschemas/order.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# A nested schema to show what each registration item contains
class RegistrationItem(BaseModel):
    registration_id: int
    course_id: int
    course_title: str
    price: float

class OrderCreate(BaseModel):
    """If you ever want to create an order directly 
       without going through public_register."""
    user_id: int
    total_amount: float
    status: Optional[str] = "pending"
    

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[RegistrationItem] = []

    class Config:
        from_attributes = True
