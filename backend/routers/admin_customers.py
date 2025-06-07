from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.user import crud_user
from backend.models.user import User
from backend.pydanticschemas.user import UserResponse, UserCreate
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/customers", tags=["Admin Customers"])


@router.get("/", response_model=List[UserResponse])
async def list_customers(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of customers."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    query = db.query(User)
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_user.delete(db, user_id)
    return {"detail": f"User with ID {user_id} deleted."}


@router.put("/{user_id}", response_model=UserResponse)
async def update_customer(
    user_id: int,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_user.update(db, user_id, user_in)
