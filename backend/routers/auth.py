# backend/routers/auth.py

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, logger, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.blacklisted_tokens import BlacklistedToken
from backend.models.order import Order
from backend.models.user import User
from backend.pydanticschemas.auth import LoginForm
from backend.pydanticschemas.user import UserCreate, UserResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates") # Adjust path

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

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Reads JWT from the HttpOnly cookie named 'access_token'.
    Decodes it, fetches user from DB, or raises 401 if invalid.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user

## 3.2 Login Endpoint

@auth_router.post("/login")
def login(response: Response, request: Request, form_data: LoginForm, db: Session = Depends(get_db)):
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
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",
        samesite="strict",  # or "lax"
        secure=False  # set to True in production with HTTPS
    )
    # Generate a CSRF token
    csrf_token = secrets.token_hex(32)
    # Set the CSRF token as a cookie (accessible by JavaScript)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=True,  # Must be accessible by JavaScript for inclusion in headers
        path="/",
        samesite="strict",
        secure=False  # Set to True in production with HTTPS
    )

    # Set session data (store the user's ID)
    request.session["user_id"] = user.id
    
    # Check for a pending or unpaid order for the user
    pending_order = db.query(Order).filter(
        Order.user_id == user.id,
        Order.status.in_(["pending", "unpaid"])  # customize as needed
    ).first()

    pending_order_id = pending_order.id if pending_order else None

   
    # If a next URL is provided, handle order association etc.
    next_url = request.query_params.get("next")
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
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    elif next_url:
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    
     # Return JSON so the front-end can decide how to redirect
    return {
        "detail": "Login successful",
        "user_id": user.id,
        "role": user.role,
        "pending_order_id": pending_order_id
    }


## 3.3 Logout Endpoint
@auth_router.post("/logout")
async def logout(
    request: Request, 
    response: Response, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    x_csrf_token: str = Header(None)
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
    if not csrf_token_cookie or csrf_token_cookie != x_csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # Blacklist Token
    blacklisted_token = BlacklistedToken(token=access_token)
    db.add(blacklisted_token)
    db.commit()

    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    
    # Clear session data
    request.session.clear()

    return response


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