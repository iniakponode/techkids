# backend/models/order.py

from backend.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # If a user is deleted => remove referencing Orders
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    total_amount = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders", passive_deletes=True)

    # Deleting this order => remove referencing Registrations
    items = relationship("Registration", back_populates="order", cascade="all, delete-orphan", passive_deletes=True)

    # 1-to-1 or 1-to-many Payment Relationship, typically 1-to-1
    payment = relationship("Payment", back_populates="order", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return (f"<Order(id={self.id}, user_id={self.user_id}, "
                f"total_amount={self.total_amount}, status={self.status})>")