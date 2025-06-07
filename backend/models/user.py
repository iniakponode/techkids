from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
   # Our role field: (Student, Parent, Teacher, Organisation, Admin)
    role = Column(String(20), default="student")  
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For account verification
    verification_token = Column(String(255), nullable=True)  # For account verification
    password_reset_token = Column(String(255), nullable=True)  # For password reset
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    # payment = relationship("Payment", back_populates="user")
