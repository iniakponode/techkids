# backend/pydanticschemas/payment.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    order_id: int
    transaction_id: Optional[str]
    amount: float

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    transaction_id: str
    amount: float
    status: str
    payment_date: datetime

class PaymentInitRequest(BaseModel):
    order_id: int
    email: str

    class Config:
        from_attributes = True