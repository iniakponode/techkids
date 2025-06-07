"""
Paystack Service Integration

This module provides helper functions to interact with the Paystack API:
- Initialize a transaction for payment (with 2 retries)
- Verify a transaction after payment (with 2 retries)

Environment Variables Required:
------------------------------
- PAYSTACK_SECRET_KEY : Your secret key from Paystack (test or live key).
- PAYSTACK_BASE_URL   : Base URL for Paystack API. Defaults to "https://api.paystack.co".

Usage:
------
1. Call initialize_transaction(...) with user email, amount in kobo, a callback URL,
   and a unique reference for the transaction. This returns a JSON response from Paystack
   containing an `authorization_url` which the user should be redirected to in order to complete payment.

2. After payment, Paystack redirects (or you can manually check) to your callback
   with the `reference`. Use verify_transaction(...) to confirm the status of the transaction.
   This returns a JSON object indicating success or failure.

References:
-----------
- Paystack API Docs: https://paystack.com/docs/api
"""

import os
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout
from fastapi import HTTPException, status

load_dotenv()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "")
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")


def initialize_transaction(email: str, amount_kobo: int, callback_url: str, reference: str) -> dict:
    """
    Initialize a Paystack transaction with up to 2 retries on network/timeout errors.

    Parameters
    ----------
    email : str
        The customer's email address.
    amount_kobo : int
        The amount to be charged, in Kobo (1 NGN = 100 Kobo).
    callback_url : str
        The URL to which Paystack will redirect after payment is completed or cancelled.
    reference : str
        A unique reference string for this transaction.

    Returns
    -------
    dict
        A JSON response from Paystack containing data such as the authorization URL
        where the user should be redirected to make payment. The "status" field indicates
        whether the initialization was successful (True/False).

    Raises
    ------
    HTTPException
        - 400 if Paystack returns a 4xx error or fails with an error message.
        - 502 if there's a network error, timeout, or we exhaust retries.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "callback_url": callback_url,
        "reference": reference,
    }

    attempts = 2
    for attempt in range(attempts):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()  # Raise for 4xx/5xx
            data = resp.json()

            # If "status" is False, Paystack is indicating an error
            if not data.get("status"):
                # E.g. { "status": false, "message": "Invalid key" }
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Paystack init error: {data.get('message')}"
                )
            return data

        except Timeout:
            # Retry on timeout
            if attempt < attempts - 1:
                continue
            # If final attempt fails, raise 502
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Paystack timeout after multiple attempts."
            )

        except RequestException as e:
            # Could be a connection error, DNS error, 4xx/5xx w/ no JSON, etc.
            if attempt < attempts - 1:
                continue
            # If final attempt fails, raise 502
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error contacting Paystack: {str(e)}"
            )


def verify_transaction(reference: str) -> dict:
    """
    Verify a Paystack transaction with up to 2 retries on network/timeout errors.

    After the user completes or cancels a payment,
    Paystack can redirect with a reference, or you
    can otherwise retrieve the reference. Then you
    call this endpoint to confirm the final status
    of the transaction on Paystack's side.

    Parameters
    ----------
    reference : str
        The unique transaction reference used during initialization.

    Returns
    -------
    dict
        A JSON response from Paystack indicating the result.
        The "status" field indicates success (True/False),
        and `data.status` typically shows "success" if the payment
        was successful.

    Raises
    ------
    HTTPException
        - 400 if Paystack returns a 4xx error or fails with an error message.
        - 502 if there's a network error, timeout, or we exhaust retries.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    attempts = 2
    for attempt in range(attempts):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("status"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Paystack verify error: {data.get('message')}"
                )
            return data

        except Timeout:
            if attempt < attempts - 1:
                continue
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Paystack verification timeout after multiple attempts."
            )

        except RequestException as e:
            if attempt < attempts - 1:
                continue
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error verifying Paystack payment: {str(e)}"
            )
