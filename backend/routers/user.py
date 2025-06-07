from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.pydanticschemas.user import UserCreate, UserResponse
from backend.models.user import User
from backend.core.database import get_db
from passlib.hash import bcrypt
from backend.routers.auth import pwd_context

router = APIRouter()

# Endpoint to create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    """
    # Check if the email is already registered
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=bcrypt.hash(user.password),  # Hash the password
        role="student",  # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    1. Check if email is already in use
    2. Hash password
    3. Insert new user
    4. Return user data
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



# Endpoint to retrieve a user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by their ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


# Simulating an email sending function (replace with a proper email integration)
def send_email(to: str, subject: str, body: str):
    print(f"Sending email to {to}: {subject}\n{body}")


# 1. Get User by Email
@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Retrieve user details by email.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found.",
        )
    return user


# 2. Account Verification
@router.post("/verify-account", response_model=str)
def verify_account(token: str, db: Session = Depends(get_db)):
    """
    Verify a user's account using a unique token.
    """
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired verification token.",
        )
    
    # Mark the user as verified
    user.is_verified = True
    user.verification_token = None  # Clear the token after use
    db.commit()
    return "Account successfully verified!"


# 3. Password Reset
@router.post("/reset-password", response_model=str)
def reset_password(email: str, new_password: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Reset a user's password securely.
    If a token is provided, use it to validate the password reset process.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found.",
        )
    
    # If a token is required for resetting the password
    if token:
        if user.password_reset_token != token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password reset token.",
            )
    
    # Update the password
    user.password_hash = bcrypt.hash(new_password)
    user.password_reset_token = None  # Clear the token after use
    db.commit()
    return "Password successfully reset!"