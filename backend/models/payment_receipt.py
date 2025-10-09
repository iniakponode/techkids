from datetime import datetime
import secrets

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from backend.core.database import Base


class PaymentReceipt(Base):
    """Immutable snapshot of a completed payment for student access."""

    __tablename__ = "payment_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NGN", nullable=False)
    payment_date = Column(DateTime, nullable=False)
    line_items = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="payment_receipts")
    order = relationship("Order", backref="payment_receipts")
    payment = relationship("Payment", backref="receipt", uselist=False)

    @staticmethod
    def generate_receipt_number() -> str:
        """Generate a short, human-readable receipt number."""

        return f"RC-{secrets.token_hex(4).upper()}"
