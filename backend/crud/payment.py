from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from backend.models.payment import Payment
from backend.pydanticschemas.payment import PaymentCreate, PaymentResponse
import logging

logger = logging.getLogger(__name__)


class CRUDPayment:
    """
    CRUD operations for Payment.

    Methods:
    - **create**: Adds a new Payment record.
    - **get_by_id**: Retrieves a Payment by ID.
    - **get_all**: Retrieves all Payments.
    - **update**: Updates a Payment record.
    - **delete**: Deletes a Payment record.
    """

    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: PaymentCreate) -> Payment:
        """
        Create a new Payment.
        """
        new_payment = self.model(**obj_in.dict())
        db.add(new_payment)
        try:
            db.commit()
            logger.info(f"Created Payment for User ID: {obj_in.user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating Payment: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating Payment.")
        db.refresh(new_payment)
        return new_payment

    def get_by_id(self, db: Session, payment_id: int) -> Optional[Payment]:
        """
        Retrieve a Payment by ID.
        """
        payment = db.query(self.model).filter(self.model.id == payment_id).first()
        if not payment:
            logger.warning(f"Payment with ID {payment_id} not found.")
        return payment

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Retrieve all Payments.
        """
        payments = db.query(self.model).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(payments)} payments.")
        return payments

    def update(self, db: Session, payment_id: int, obj_in: PaymentCreate) -> Payment:
        """
        Update a Payment by ID.
        """
        payment = self.get_by_id(db, payment_id)
        if not payment:
            raise HTTPException(
                status_code=404, detail=f"Payment with ID {payment_id} not found."
            )
        for key, value in obj_in.dict().items():
            setattr(payment, key, value)
        db.add(payment)
        try:
            db.commit()
            logger.info(f"Updated Payment with ID: {payment_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Payment: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating Payment.")
        db.refresh(payment)
        return payment

    def delete(self, db: Session, payment_id: int) -> Optional[Payment]:
        """
        Delete a Payment by ID.
        """
        payment = self.get_by_id(db, payment_id)
        if not payment:
            raise HTTPException(
                status_code=404, detail=f"Payment with ID {payment_id} not found."
            )
        db.delete(payment)
        try:
            db.commit()
            logger.info(f"Deleted Payment with ID: {payment_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting Payment: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting Payment.")
        return payment


# Initialize CRUD instance for Payment
crud_payment = CRUDPayment(Payment)
