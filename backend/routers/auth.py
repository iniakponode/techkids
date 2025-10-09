# backend/routers/auth.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    logger,
    status,
)
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy.orm import Session
import secrets

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.blacklisted_tokens import BlacklistedToken
from backend.models.order import Order
from backend.models.user import User
from backend.pydanticschemas.auth import LoginForm
from backend.pydanticschemas.user import UserCreate, UserResponse
from fastapi.responses import JSONResponse

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# This is used only by the "login" route, since we need to accept user credentials.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def _get_user_from_token(
    token: Optional[str],
    db: Session,
    *,
    raise_errors: bool = True,
) -> Optional[User]:
    """Validate a JWT and return the associated user if present."""

    if not token:
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        return None

    # Check whether the token has been revoked.
    blacklisted = (
        db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    )
    if blacklisted:
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired, please log in again",
            )
        return None
    except JWTError:
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
            )
        return None

    email: Optional[str] = payload.get("sub")
    if not email:
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
            )
        return None

    user = db.query(User).filter(User.email == email).first()
    if not user and raise_errors:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency to require a logged-in user."""

    user = _get_user_from_token(request.cookies.get("access_token"), db, raise_errors=True)
    assert user is not None  # for type checkers; raise_errors=True guarantees non-None
    return user


async def get_optional_user(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    """Return the authenticated user if present; otherwise ``None``."""

    return _get_user_from_token(request.cookies.get("access_token"), db, raise_errors=False)


def _safe_redirect_target(target: Optional[str]) -> Optional[str]:
    """Ensure redirect targets remain within this application."""

    if not target:
        return None

    target = target.strip()
    if target.startswith(("http://", "https://", "//")):
        return None

    if not target.startswith("/"):
        target = f"/{target}"

    return target

## 3.2 Login Endpoint

@auth_router.post("/login")
def login(request: Request, form_data: LoginForm, db: Session = Depends(get_db)):
    """
    Authenticates a user using the provided credentials.
    On successful login:
      - Generates an access token (JWT) and sets it in an HttpOnly cookie.
      - Generates a CSRF token and sets it in a cookie (accessible by JavaScript).
      - Optionally, pass the CSRF token to your frontend (e.g., via a meta tag).
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )

    access_token = create_access_token(data={"sub": user.email})
    csrf_token = secrets.token_hex(32)

    secure_cookie = settings.ENVIRONMENT.lower() == "production"

    response_payload = {
        "detail": "Login successful",
        "user_id": user.id,
        "role": user.role,
    }
    
    # Check for a pending or unpaid order for the user
    pending_order = db.query(Order).filter(
        Order.user_id == user.id,
        Order.status.in_(["pending", "unpaid"])  # customize as needed
    ).first()

    pending_order_id = pending_order.id if pending_order else None

    response_payload["pending_order_id"] = pending_order_id

    # If a next URL is provided, handle order association etc.
    next_url = _safe_redirect_target(form_data.next or request.query_params.get("next"))
    order_id_param = request.query_params.get("order_id")
    if next_url and order_id_param:
        try:
            order_id = int(order_id_param)
            order = db.query(Order).filter(Order.id == order_id).first()
            if order and order.user_id is None:
                order.user_id = user.id
                db.commit()
                logger.info(f"Order {order_id} associated with user {user.id} after login.")
        except ValueError:
            logger.warning(f"Invalid order_id parameter: {order_id_param}")
        response_payload["redirect_url"] = next_url
    elif next_url:
        response_payload["redirect_url"] = next_url
    elif user.role == "admin":
        response_payload["redirect_url"] = "/admin/dashboard"
    elif pending_order_id:
        response_payload["redirect_url"] = f"/payment?order={pending_order_id}"
    else:
        response_payload["redirect_url"] = "/"

    # Set session data (store the user's ID)
    request.session["user_id"] = user.id

    response = JSONResponse(response_payload)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",
        samesite="lax",
        secure=secure_cookie,
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        path="/",
        samesite="lax",
        secure=secure_cookie,
    )

    return response


## 3.3 Logout Endpoint
@auth_router.post("/logout")
async def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_csrf_token: str = Header(None),
):
    """
    Logs out the current user by clearing the access token cookie and blacklisting the token.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found")

    # CSRF Protection
    csrf_token_cookie = request.cookies.get("csrf_token")
    csrf_token_header = x_csrf_token
    if not csrf_token_cookie or not csrf_token_header or csrf_token_cookie != csrf_token_header:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # Blacklist Token (idempotent)
    existing_token = (
        db.query(BlacklistedToken).filter(BlacklistedToken.token == access_token).first()
    )
    if not existing_token:
        try:
            bind = db.get_bind()
            if bind and bind.dialect.name == "mysql":
                db.execute(
                    text(
                        "INSERT IGNORE INTO blacklisted_tokens (token) VALUES (:token)"
                    ),
                    {"token": access_token},
                )
            else:
                blacklisted_token = BlacklistedToken(token=access_token)
                db.add(blacklisted_token)

            db.commit()
        except IntegrityError:
            db.rollback()

    logout_response = JSONResponse({"detail": "Logged out successfully"})
    logout_response.delete_cookie(key="access_token", path="/")
    logout_response.delete_cookie(key="csrf_token", path="/")

    # Clear session data
    request.session.clear()

    return logout_response


## 3.4 Signup Endpoint (If separate from the combined Registration)

@auth_router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    1. Check if email exists
    2. Create user with hashed password
    3. Generate a verification token (optional step)
    4. Return the user
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_pw = hash_password(user.password)
    verification_token = secrets.token_urlsafe(32)  # or any random generator

    new_user = User(
        email=user.email,
        password_hash=hashed_pw,
        role=user.role,
        is_verified=False, # Set to False initially
        verification_token=verification_token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email here (optional)
    # send_verification_email(new_user.email, verification_token)

    return new_user

## 3.5 Email Verification Endpoint

@auth_router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"detail": "Email verified successfully"}


@auth_router.post("/admin/register", response_model=UserResponse)
def admin_register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers an admin user.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_pw,
        role="admin",  # Explicitly set role to admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# @auth_router.post("admin/login")
# def login(response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     """
#     Handles login for all user roles. Redirects admins to the dashboard.
#     """
#     user = db.query(User).filter(User.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Incorrect email or password."
#         )

#     access_token = create_access_token(data={"sub": user.email})
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,
#         samesite="strict",
#         secure=False
#     )

#     if user.role == "admin":
#         return RedirectResponse(url="/auth/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

#     next_url = request.query_params.get("next")
#     if next_url:
#         return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)

#     return {"detail": "Login successful", "user_id": user.id, "role": user.role}