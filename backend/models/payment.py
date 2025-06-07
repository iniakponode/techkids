from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from backend.core.database import Base
from sqlalchemy.orm import relationship


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    # If an Order is deleted, remove referencing Payments
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    transaction_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    payment_date = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payment", passive_deletes=True)

    def __repr__(self):
        return (f"<Payment(id={self.id}, amount={self.amount}, "
                f"status={self.status}, payment_date={self.payment_date})>")