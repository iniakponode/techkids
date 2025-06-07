from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.hash import bcrypt
from typing import List, Optional
from backend.models.user import User
from backend.pydanticschemas.user import UserCreate, UserResponse
from uuid import UUID
import logging
import secrets
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class CRUDUser:
    """
    CRUD operations for User.

    Methods:
    - **create**: Adds a new User record.
    - **get_by_id**: Retrieves a User by UUID.
    - **get_by_email**: Retrieves a User by email.
    - **get_all**: Retrieves all Users.
    - **update**: Updates a User record.
    - **delete**: Deletes a User record.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def __init__(self, model):
        self.model = model

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
    
    def create(self, db: Session, obj_in: UserCreate) -> User:
        """
        Create a new User in the database.
        """
        if db.query(self.model).filter(self.model.email == obj_in.email).first():
            raise HTTPException(status_code=400, detail="Email is already registered.")

        hashed_password = bcrypt.hash(obj_in.password)
        new_user = self.model(
            email=obj_in.email,
            password_hash=hashed_password,
            role=obj_in.role if obj_in.role else "student",
        )
        db.add(new_user)
        try:
            db.commit()
            logger.info(f"Created User with email: {obj_in.email}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating User: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating User.")
        
        db.refresh(new_user)
        return new_user

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a User by their ID.
        """
        user = db.query(self.model).filter(self.model.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
        return user

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve a User by their email.
        """
        user = db.query(self.model).filter(self.model.email == email).first()
        if not user:
            logger.warning(f"User with email {email} not found.")
        return user

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all Users.
        """
        users = db.query(self.model).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(users)} users.")
        return users

    def update(self, db: Session, user_id: int, obj_in: UserCreate) -> User:
        """
        Update a User's details by ID.
        """
        user = self.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

        user.email = obj_in.email
        user.role = obj_in.role if obj_in.role else user.role
        user.password_hash = bcrypt.hash(obj_in.password)
        db.add(user)
        try:
            db.commit()
            logger.info(f"Updated User with ID: {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating User: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating User.")
        
        db.refresh(user)
        return user

    def delete(self, db: Session, user_id: int) -> Optional[User]:
        """
        Delete a User by ID.
        """
        user = self.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")
        
        db.delete(user)
        try:
            db.commit()
            logger.info(f"Deleted User with ID: {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting User: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting User.")
        
        return user


# Initialize the CRUDUser instance
crud_user = CRUDUser(User)
