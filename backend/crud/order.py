# backend/crud/order.py

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.order import Order
from backend.models.registration import Registration
from backend.models.course import Course
from backend.pydanticschemas.order import OrderCreate, OrderResponse, RegistrationItem

logger = logging.getLogger(__name__)

class CRUDOrder:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: OrderCreate) -> Order:
        new_order = self.model(**obj_in.dict())
        db.add(new_order)
        try:
            db.commit()
            logger.info(f"Created Order for User ID: {obj_in.user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating Order: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error creating Order."
            )
        db.refresh(new_order)
        return new_order

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        order = db.query(self.model).filter(self.model.id == order_id).first()
        return order

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        orders = db.query(self.model).offset(skip).limit(limit).all()
        return orders

    def update(self, db: Session, order_id: int, obj_in: OrderCreate) -> Order:
        order = self.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found."
            )
        # update fields
        for key, value in obj_in.dict(exclude_unset=True).items():
            setattr(order, key, value)
        db.add(order)
        try:
            db.commit()
            logger.info(f"Updated Order ID: {order_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Order: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error updating Order."
            )
        db.refresh(order)
        return order

    def delete(self, db: Session, order_id: int) -> Optional[Order]:
        order = self.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found."
            )
        db.delete(order)
        try:
            db.commit()
            logger.info(f"Deleted Order with ID: {order_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting Order: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting Order.")
        return order

    def get_order_response(self, db: Session, order_id: int) -> OrderResponse:
        """
        Returns an OrderResponse schema including the nested items 
        (with course title and price).
        """
        order = self.get_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")

        # Build the list of RegistrationItem
        registration_items = []
        for reg in order.items:  # order.items is the list of Registration objects
            course = db.query(Course).filter(Course.id == reg.course_id).first()
            if course:
                registration_items.append(
                    RegistrationItem(
                        registration_id=reg.id,
                        course_id=course.id,
                        course_title=course.title,
                        price=course.price
                    )
                )

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            items=registration_items
        )

crud_order = CRUDOrder(Order)
