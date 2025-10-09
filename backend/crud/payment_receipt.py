from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.payment_receipt import PaymentReceipt


class CRUDPaymentReceipt:
    """Simple CRUD helpers for payment receipt records."""

    def __init__(self, model: type[PaymentReceipt]):
        self.model = model

    def create(
        self,
        db: Session,
        *,
        user_id: Optional[int],
        order_id: int,
        payment_id: int,
        amount: float,
        currency: str,
        payment_date: datetime,
        line_items: list[dict],
    ) -> PaymentReceipt:
        receipt = self.model(
            receipt_number=self.model.generate_receipt_number(),
            user_id=user_id,
            order_id=order_id,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            payment_date=payment_date,
            line_items=line_items,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    def get_by_payment(self, db: Session, payment_id: int) -> Optional[PaymentReceipt]:
        return (
            db.query(self.model)
            .filter(self.model.payment_id == payment_id)
            .first()
        )

    def list_for_user(self, db: Session, user_id: int) -> List[PaymentReceipt]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.payment_date.desc())
            .all()
        )


crud_payment_receipt = CRUDPaymentReceipt(PaymentReceipt)
