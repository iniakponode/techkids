from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from backend.pydanticschemas.registration import PublicRegistrationRequest
from backend.routers.auth import pwd_context
from backend.models.course import Course
from backend.models.order import Order
from backend.models.registration import Registration
from backend.models.user import User
from backend.core.database import get_db
from backend.utils.auth_utils import create_or_get_user, set_jwt_cookie_for_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/public-register")
def public_register(
    data: PublicRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    1. Create & commit the user in DB (no rollback if payment fails).
    2. Create & commit the order (status="pending").
    3. Create and link the registration entries to the order.
    4. Return {order_id, total_cost} to the frontend.
    """
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        if not pwd_context.verify(data.password, existing_user.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect password for existing account.")
        user = existing_user
    else:
        hashed_pw = pwd_context.hash(data.password)
        user = User(
            email=data.email,
            password_hash=hashed_pw,
            role=data.role,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    total_cost = 0.0
    courses: List[Course] = []
    for course_id in data.course_ids:
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            total_cost += course.price
            courses.append(course)

    if not courses:
        raise HTTPException(status_code=400, detail="Please select at least one course to continue.")

    new_order = Order(
        user_id=user.id,
        total_amount=total_cost,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for course in courses:
        registration = Registration(
            user_id=user.id,
            course_id=course.id,
            order_id=new_order.id,
            fullName=data.fullName,
            phone=data.phone,
            status="pending",
        )
        db.add(registration)

    db.commit()

    logger.info(
        "User %s registered. Order %s created with %s courses.",
        user.email,
        new_order.id,
        len(courses),
    )

    return {
        "order_id": new_order.id,
        "total_cost": total_cost
    }