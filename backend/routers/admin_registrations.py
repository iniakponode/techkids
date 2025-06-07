from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.registration import crud_registration
from backend.models.payment import Payment
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/registrations", tags=["Admin Registrations"])


@router.get("/", response_model=List[dict])
def list_registrations(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of registrations."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    regs = crud_registration.get_all(db, skip=skip, limit=limit)
    result = []
    for reg in regs:
        payment = db.query(Payment).filter(Payment.order_id == reg.order_id).first()
        result.append({
            "id": reg.id,
            "fullName": reg.fullName,
            "phone": reg.phone,
            "user_id": reg.user_id,
            "course_id": reg.course_id,
            "order_id": reg.order_id,
            "status": reg.status,
            "is_verified": reg.is_verified,
            "payment_status": payment.status if payment else "pending",
            "registered_at": reg.registered_at,
        })
    return result


@router.delete("/delete/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_registration.delete(db, registration_id)
    return {"detail": f"Registration {registration_id} deleted"}
