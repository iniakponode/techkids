from datetime import datetime
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)

class CategoryCreate(CategoryBase):
    pass

class CategorySchema(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
