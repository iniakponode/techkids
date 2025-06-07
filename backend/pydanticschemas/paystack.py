from pydantic import BaseModel

class PaystackInitRequest(BaseModel):
    order_id: int
    email: str