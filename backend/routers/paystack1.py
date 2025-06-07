import json
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import urllib.parse

from backend.core.database import get_db
from backend.models.order import Order
from backend.models.payment import Payment
from backend.models.registration import Registration
from backend.services.paystack_service import initialize_transaction, verify_transaction
from backend.pydanticschemas.payment import PaymentInitRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paystack", tags=["Paystack"])

"""
Paystack Router Module

This module implements the integration with Paystack for payment processing.
It provides endpoints to initialize a Paystack transaction and to verify a transaction.

Features:
    - Validates an Order before initializing payment.
    - Creates a Payment record with status "pending" (without rolling back User/Order on payment failure).
    - Calls Paystack's initialize_transaction() to obtain an authorization URL.
    - Verifies the transaction via verify_transaction(), and if successful, marks Payment as "completed"
      and Order as "paid". Otherwise, marks Payment as "failed".
    - Redirects the user back to the registration page with query parameters containing payment details
      (order_id, amount, payment_date) or an error message.

Environment Variables:
    - PAYSTACK_SECRET_KEY: Your Paystack secret key.
    - PAYSTACK_BASE_URL: Base URL for Paystack API (default: "https://api.paystack.co").

Usage:
    - POST /api/paystack/init: Initializes a payment.
    - GET   /api/paystack/verify: Verifies a payment and updates records accordingly, then redirects.
"""

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import urllib.parse
import json  # Import the json module

from backend.core.database import get_db
from backend.models.order import Order
from backend.models.payment import Payment
from backend.models.registration import Registration
from backend.services.paystack_service import initialize_transaction, verify_transaction
from backend.pydanticschemas.payment import PaymentInitRequest
# PaymentInitRequest is a Pydantic model with fields: order_id: int, email: str

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paystack", tags=["Paystack"])


@router.post("/init")
def paystack_init_payment(
    payload: PaymentInitRequest,
    db: Session = Depends(get_db)
):
    """
    Initializes a Paystack payment for the given Order.

    Steps:
      1. Validate that the Order exists and is not already paid.
      2. Convert the Order's total_amount to Kobo.
      3. Generate a unique reference (e.g. "TX-<order_id>-<uuid>").
      4. Create a new Payment record with status "pending".
      5. Call initialize_transaction() from the paystack_service to get the authorization_url.
      6. Return a JSON response with the authorization_url, reference, and a success message.
    """
    order_id = payload.order_id
    email = payload.email

    # 1) Validate Order
    order_obj = db.query(Order).filter(Order.id == order_id).first()
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found.")
    if order_obj.status.lower() == "paid":
        raise HTTPException(status_code=400, detail="Order is already paid.")

    # 2) Convert total amount to Kobo
    amount_kobo = int(order_obj.total_amount * 100)
    if amount_kobo < 100:
        raise HTTPException(status_code=400, detail="Order amount is too small or invalid.")

    # 3) Generate unique reference
    reference = f"TX-{order_obj.id}-{uuid.uuid4()}"

    # 4) Create a new Payment record with "pending" status
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

    # 5) Do NOT create registration records again. Just fetch the existing ones.
    registrations = db.query(Registration).filter(Registration.order_id == order_obj.id).all()
    if not registrations:
        raise HTTPException(status_code=400, detail="No courses registered for this order.")

    # 6) Call Paystack to initialize the transaction
    callback_url = "http://127.0.0.1:8002/api/paystack/verify"  # Adjust for production
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
    reference: str,
    db: Session = Depends(get_db)
):
    """
    Verifies a Paystack payment using the transaction reference.

    Steps:
      1. Call verify_transaction(reference) from the paystack_service.
      2. If verification is successful:
                 - Update Payment.status to "completed" and set payment_date.
                 - Update Order.status to "paid".
                 - Commit changes.
                 - Redirect the user to the registration page with query parameters:
                  payment_success=true, order_id, amount, payment_date, and courses.
      3. If verification fails:
                 - Update Payment.status to "failed".
                 - Commit changes.
                 - Redirect the user to the registration page with query parameters indicating failure.
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

    # Retrieve the local Payment record by reference
    payment = db.query(Payment).filter(Payment.transaction_id == reference).first()
    if not payment:
        logger.error(f"No Payment record found for reference={reference}")
        return RedirectResponse(url="/registration?payment_error=payment_not_found", status_code=302)

    # Retrieve the corresponding Order
    order_obj = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order_obj:
        logger.error(f"No Order found for Payment.order_id={payment.order_id}")
        return RedirectResponse(url="/registration?payment_error=order_not_found", status_code=302)

    # Fetch registered courses for the order
    registrations = db.query(Registration).filter(Registration.order_id == order_obj.id).all()
    courses = [{"title": reg.course.title, "price": reg.course.price} for reg in registrations]

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

        # Serialize the courses list to a JSON string
        encoded_courses = urllib.parse.quote_plus(json.dumps(courses))
        redirect_url = f"/registration?payment_success=true&order_id={order_obj.id}&amount={payment.amount}&payment_date={paid_at_str}&courses={encoded_courses}"
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