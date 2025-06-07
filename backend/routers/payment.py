# backend/routers/payment.py

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.models.order import Order
from backend.models.payment import Payment
from backend.pydanticschemas.payment import PaymentCreate, PaymentResponse
from backend.core.database import get_db
from backend.crud.payment import crud_payment
from backend.crud.order import crud_order  # If we need to read the Order
# from .auth import get_current_user  # if you want to ensure user is logged in

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """
    Create a Payment for a given order_id.
    - Validates the order
    - Could integrate external payment gateway (Paystack, PayPal, etc.)
    - On success, sets order.status = "paid"
    """
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    if order.status.lower() == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    # (Placeholder) If you want to do the real integration with Paystack/PayPal:
    # 1. Use payment.cardNumber, payment.cardName, etc. to call the external service.
    # 2. If external payment fails, raise an HTTPException with details.
    # 3. If successful, proceed.

    # For now, we assume the payment is successful:
    new_payment = Payment(
        order_id=order.id,
        transaction_id=str(uuid4()),
        amount=order.total_amount,  # or payment.amount if you allow partial
        status="completed",
        payment_date=datetime.utcnow(),
    )
    db.add(new_payment)

    # Mark order as "paid"
    order.status = "paid"
    try:
        db.commit()
        db.refresh(new_payment)
        logger.info(f"Payment successful. Payment ID: {new_payment.id}, Order ID: {order.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating Payment.")
    
    return new_payment

@router.get("/", response_model=List[PaymentResponse])
def get_payments(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all payments (for admin).
    """
    return crud_payment.get_all(db=db, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_by_id(payment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a payment by ID.
    """
    payment = crud_payment.get_by_id(db=db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found.",
        )
    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, updated_payment: PaymentCreate, db: Session = Depends(get_db)):
    """
    Update a payment by ID.
    """
    return crud_payment.update(db=db, payment_id=payment_id, obj_in=updated_payment)

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """
    Delete a payment by ID.
    """
    crud_payment.delete(db=db, payment_id=payment_id)
    return {"message": f"Payment with ID {payment_id} successfully deleted."}
