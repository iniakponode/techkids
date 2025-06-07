"""
Paystack Router Module

This module implements the integration with Paystack for payment processing.
It provides endpoints to initialize a Paystack transaction and to verify a transaction.

Features:
    - Validates an Order before initializing payment.
    - Creates a Payment record with status "pending" (without rolling back User/Order on payment failure).
    - Calls Paystack's initialize_transaction() to obtain an authorization URL.
    - Verifies the transaction via verify_transaction(), and if successful, marks Payment as "completed"
      and Order as "paid".
    - Redirects the user back to the registration page with a temporary token and order ID upon successful payment.
    - Provides an API endpoint to securely retrieve payment success details using the token.

Environment Variables:
    - PAYSTACK_SECRET_KEY: Your Paystack secret key.
    - PAYSTACK_BASE_URL: Base URL for Paystack API (default: "https://api.paystack.co").

Usage:
    - POST /api/paystack/init: Initializes a payment.
    - GET   /api/paystack/verify: Verifies a payment, generates a token, and redirects.
    - GET   /api/paystack/success_details/{token}: Retrieves payment success details.
"""

import os
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from backend.core.database import get_db
from backend.models.order import Order
from backend.models.payment import Payment
from backend.models.registration import Registration
from backend.services.paystack_service import initialize_transaction, verify_transaction
from backend.pydanticschemas.payment import PaymentInitRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paystack", tags=["Paystack"])

# In-memory storage for temporary tokens and payment data (replace with a more secure mechanism like Redis or a database)
TEMP_PAYMENT_DATA: Dict[str, Dict[str, Any]] = {}

@router.post("/init")
def paystack_init_payment(
    payload: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """
    Initializes a Paystack payment for the given Order.
    ... (rest of the docstring as before)
    """
    order_id = payload.order_id
    email = payload.email

    order_obj = db.query(Order).filter(Order.id == order_id).first()
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found.")
    if order_obj.status.lower() == "paid":
        raise HTTPException(status_code=400, detail="Order is already paid.")

    amount_kobo = int(order_obj.total_amount * 100)
    if amount_kobo < 100:
        raise HTTPException(status_code=400, detail="Order amount is too small or invalid.")

    reference = f"TX-{order_obj.id}-{uuid.uuid4()}"

    new_payment = Payment(
        order_id=order_obj.id,
        transaction_id=reference,
        amount=order_obj.total_amount,
        status="pending",
        payment_date=datetime.utcnow()
    )
    db.add(new_payment)

    try:
        db.commit()
        db.refresh(new_payment)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Payment record: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create payment record.")

    registrations = db.query(Registration).filter(Registration.order_id == order_obj.id).all()
    if not registrations:
        raise HTTPException(status_code=400, detail="No courses registered for this order.")

    # callback_url = "http://127.0.0.1:8002/api/paystack/verify"  # Adjust for production
    # Use the PAYSTACK_CALLBACK_URL env variable, or default to a local URL for development.
    callback_url = os.getenv("PAYSTACK_CALLBACK_URL", "http://localhost:8002/api/paystack/verify")
    try:
        paystack_response = initialize_transaction(
            email=email,
            amount_kobo=amount_kobo,
            callback_url=callback_url,
            reference=reference
        )
    except HTTPException as e:
        logger.error(f"Paystack init error: {e.detail}")
        raise e
    except Exception as exc:
        logger.error(f"Unexpected error calling Paystack init: {str(exc)}")
        raise HTTPException(status_code=500, detail="Unexpected error calling Paystack.")

    if not paystack_response.get("status"):
        message = paystack_response.get("message", "Paystack initialization failed.")
        logger.error(f"Paystack init returned status=False: {message}")
        raise HTTPException(status_code=400, detail=message)

    authorization_url = paystack_response["data"]["authorization_url"]

    return {
        "authorization_url": authorization_url,
        "reference": reference,
        "message": "Payment initialized"
    }

@router.get("/verify")
def paystack_verify_payment(
    request: Request,
    reference: str,
    db: Session = Depends(get_db)
):
    """
    Verifies a Paystack payment using the transaction reference.
    ... (rest of the docstring as before)
    """
    try:
        verify_resp = verify_transaction(reference)
    except HTTPException as e:
        logger.error(f"Paystack verify HTTPException: {e.detail}")
        return RedirectResponse(url=f"/registration?payment_error={e.detail}", status_code=302)
    except Exception as exc:
        logger.error(f"Unexpected error verifying Paystack: {str(exc)}")
        return RedirectResponse(url="/registration?payment_error=unexpected", status_code=302)

    if not verify_resp.get("status"):
        message = verify_resp.get("message", "Verification returned status=False")
        logger.error(f"Paystack verify error: {message}")
        return RedirectResponse(url=f"/registration?payment_error={message}", status_code=302)

    data = verify_resp["data"]
    paystack_status = data["status"]  # Expected "success" if paid

    payment = db.query(Payment).filter(Payment.transaction_id == reference).first()
    if not payment:
        logger.error(f"No Payment record found for reference={reference}")
        return RedirectResponse(url="/registration?payment_error=payment_not_found", status_code=302)

    order_obj = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order_obj:
        logger.error(f"No Order found for Payment.order_id={payment.order_id}")
        return RedirectResponse(url="/registration?payment_error=order_not_found", status_code=302)

    if paystack_status == "success":
        payment.status = "completed"
        payment.payment_date = datetime.utcnow()
        order_obj.status = "paid"
        try:
            db.commit()
            db.refresh(payment)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Payment/Order to paid: {str(e)}")
            return RedirectResponse(url="/registration?payment_error=db_commit_error", status_code=302)

        logger.info(f"Payment {payment.id} verified. Order {order_obj.id} marked paid.")
        paid_at_str = payment.payment_date.strftime("%Y-%m-%d %H:%M:%S")
        registrations = db.query(Registration).filter(Registration.order_id == order_obj.id).all()
        courses = [{"title": reg.course.title, "price": float(reg.course.price)} for reg in registrations]

        # Generate a unique token for accessing payment details
        token = str(uuid.uuid4())
        TEMP_PAYMENT_DATA[token] = {
            "order_id": order_obj.id,
            "amount": float(payment.amount),
            "payment_date": paid_at_str,
            "courses": courses
        }

        redirect_url = f"/registration?payment_success=true&order_id={order_obj.id}&token={token}"
        return RedirectResponse(url=redirect_url, status_code=302)
    else:
        payment.status = "failed"
        try:
            db.commit()
            db.refresh(payment)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Payment to failed: {str(e)}")
            return RedirectResponse(url="/registration?payment_error=db_commit_failed", status_code=302)

        logger.warning(f"Payment {payment.id} not successful. Paystack status={paystack_status}")
        redirect_url = f"/registration?payment_success=false&order_id={order_obj.id}"
        return RedirectResponse(url=redirect_url, status_code=302)

@router.get("/success_details/{token}")
def get_payment_success_details(token: str):
    """
    Retrieves payment success details using a temporary token.
    """
    if token in TEMP_PAYMENT_DATA:
        payment_data = TEMP_PAYMENT_DATA.pop(token)  # Retrieve and remove the token to prevent reuse
        return payment_data
    else:
        raise HTTPException(status_code=404, detail="Invalid or expired payment success token.")
    
    

# @router.get("/verify")
# async def paystack_verify_payment(
#     request: Request,
#     reference: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     Verifies a Paystack payment using the transaction reference.
#     ... (rest of the docstring as before)
#     """
#     try:
#         verify_resp = verify_transaction(reference)
#     except HTTPException as e:
#         logger.error(f"Paystack verify HTTPException: {e.detail}")
#         return RedirectResponse(url=f"/registration?payment_error={e.detail}", status_code=302)
#     except Exception as exc:
#         logger.error(f"Unexpected error verifying Paystack: {str(exc)}")
#         return RedirectResponse(url="/registration?payment_error=unexpected", status_code=302)

#     if not verify_resp.get("status"):
#         message = verify_resp.get("message", "Verification returned status=False")
#         logger.error(f"Paystack verify error: {message}")
#         return RedirectResponse(url=f"/registration?payment_error={message}", status_code=302)

#     data = verify_resp["data"]
#     paystack_status = data["status"]  # Expected "success" if paid

#     payment = db.query(Payment).filter(Payment.transaction_id == reference).first()
#     if not payment:
#         logger.error(f"No Payment record found for reference={reference}")
#         return RedirectResponse(url="/registration?payment_error=payment_not_found", status_code=302)

#     order_obj = db.query(Order).filter(Order.id == payment.order_id).first()
#     if not order_obj:
#         logger.error(f"No Order found for Payment.order_id={payment.order_id}")
#         return RedirectResponse(url="/registration?payment_error=order_not_found", status_code=302)

#     if paystack_status == "success":
#         payment.status = "completed"
#         payment.payment_date = datetime.utcnow()
#         order_obj.status = "paid"
#         try:
#             db.commit()
#             db.refresh(payment)
#         except Exception as e:
#             # ... error handling
#             return RedirectResponse(url="/registration?payment_error=db_commit_error", status_code=302)

#         logger.info(f"Payment {payment.id} verified. Order {order_obj.id} marked paid.")
#         paid_at_str = payment.payment_date.strftime("%Y-%m-%d %H:%M:%S")
#         registrations = db.query(Registration).filter(Registration.order_id == order_obj.id).all()
#         courses = [{"title": reg.course.title, "price": float(reg.course.price)} for reg in registrations]

#         request.session["payment_success_data"] = {
#             "order_id": order_obj.id,
#             "amount": float(payment.amount),
#             "payment_date": paid_at_str,
#             "courses": courses
#         }

#         access_token = request.cookies.get("access_token")
#         if not access_token:
#             return RedirectResponse(url=f"/auth/login?next=/registration?payment_success=true&order_id={order_obj.id}", status_code=status.HTTP_303_SEE_OTHER)
#         else:
#             # Associate the user with the order if not already associated
#             user = await get_current_user(request, db) # Use the dependency
#             if order_obj.user_id is None:
#                 order_obj.user_id = user.id
#                 db.commit()
#                 logger.info(f"Order {order_obj.id} associated with user {user.id}")
#             return RedirectResponse(url="/registration?payment_success=true", status_code=302)
#     else:
#         payment.status = "failed"
#         try:
#             db.commit()
#             db.refresh(payment)
#         except Exception as e:
#             db.rollback()
#             logger.error(f"Error updating Payment to failed: {str(e)}")
#             return RedirectResponse(url="/registration?payment_error=db_commit_failed", status_code=302)

#         logger.warning(f"Payment {payment.id} not successful. Paystack status={paystack_status}")
#         redirect_url = f"/registration?payment_success=false&order_id={order_obj.id}"
#         return RedirectResponse(url=redirect_url, status_code=302)

# @router.get("/success_details/{token}")
# def get_payment_success_details(token: str):
#     """
#     Retrieves payment success details using a temporary token.
#     """
#     if token in TEMP_PAYMENT_DATA:
#         payment_data = TEMP_PAYMENT_DATA.pop(token)  # Retrieve and remove the token to prevent reuse
#         return payment_data
#     else:
#         raise HTTPException(status_code=404, detail="Invalid or expired payment success token.")