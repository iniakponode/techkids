from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class PaymentReceiptLineItem(BaseModel):
    title: str
    price: float | None = None


class PaymentReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    user_id: int | None
    order_id: int
    payment_id: int
    amount: float
    currency: str
    payment_date: datetime
    line_items: List[PaymentReceiptLineItem]

    class Config:
        from_attributes = True
