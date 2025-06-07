# backend/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.models.order import Order
from backend.crud.order import crud_order
from backend.pydanticschemas.order import OrderCreate, OrderResponse

router = APIRouter()

@router.post("/", response_model=OrderResponse)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order directly. 
    (In your flow, you often create orders in the public_register endpoint,
     but this is here if you want a direct create.)
    """
    order = crud_order.create(db, order_in)
    return crud_order.get_order_response(db, order.id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an Order by ID, including the courses in that order.
    """
    return crud_order.get_order_response(db, order_id)

@router.get("/", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    List all orders (useful for admin or debugging).
    """
    orders = crud_order.get_all(db, skip, limit)
    # Convert each to an OrderResponse
    return [crud_order.get_order_response(db, o.id) for o in orders]

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_in: OrderCreate, db: Session = Depends(get_db)):
    """
    Update an existing order (e.g. status or total_amount).
    """
    updated = crud_order.update(db, order_id, order_in)
    return crud_order.get_order_response(db, updated.id)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Delete an Order by ID (and presumably all registrations?).
    """
    # You may want to handle logic for deleting associated registrations.
    crud_order.delete(db, order_id)
    return {"detail": f"Order with ID {order_id} deleted."}