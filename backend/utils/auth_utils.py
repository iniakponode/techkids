# backend/utils/auth_utils.py

import secrets
from passlib.context import CryptContext
from backend.models.user import User
from backend.core.database import SessionLocal
from backend.routers.auth import create_access_token  # if needed
# or import from wherever you defined create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_or_get_user(data, db):
    """
    1. Check if a user with the given email already exists.
    2. If found, return the existing user.
    3. Otherwise, create a new user with hashed password, etc.
    """
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        return existing_user

    # If no user found, create a new one
    hashed_pw = pwd_context.hash(data.password)
    verification_token = secrets.token_urlsafe(32)

    new_user = User(
        email=data.email,
        password_hash=hashed_pw,
        role=data.role,
        verification_token=verification_token,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def set_jwt_cookie_for_user(user, response):
    """
    1. Create a JWT access token for the user's email.
    2. Set it in an HTTP-only cookie on the response object.
    """
    # Import create_access_token from your auth module if not already.
    from backend.routers.auth import create_access_token  

    token_data = {"sub": user.email}  # "sub" typically identifies the subject (user)
    access_token = create_access_token(token_data)

    # Set the cookie
    # Adjust 'secure=True' and 'samesite' as needed for production
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="strict"
    )

