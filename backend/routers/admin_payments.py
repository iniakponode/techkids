from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.payment import crud_payment
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/payments", tags=["Admin Payments"])


@router.get("/", response_model=List[dict])
def list_payments(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of payments."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    payments = crud_payment.get_all(db, skip=skip, limit=limit)
    return [
        {
            "id": p.id,
            "order_id": p.order_id,
            "transaction_id": p.transaction_id,
            "amount": p.amount,
            "status": p.status,
            "payment_date": p.payment_date,
        }
        for p in payments
    ]


@router.delete("/delete/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_payment.delete(db, payment_id)
    return {"detail": f"Payment {payment_id} deleted"}
