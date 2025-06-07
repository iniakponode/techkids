from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)

    # ondelete="SET NULL": Set null the Course if any Registration references it
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)

    # ondelete="CASCADE": if a User is deleted, remove referencing Registrations
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # ondelete="CASCADE": if an Order is deleted, remove referencing Registrations
    # or use "SET NULL" if you want to keep registrations but remove the link to the order
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=True)

    registered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")
    is_verified = Column(String(10), default="pending")

    # Relationships
    # No cascade or passive_deletes on the parent Course side, so we do not remove Registrations automatically
    course = relationship("Course", back_populates="registrations", passive_deletes=True)

    # The user relationship can cascade if we want user deletion => remove these
    user = relationship("User", back_populates="registrations", passive_deletes=True)

    # The order relationship can cascade if we want order deletion => remove these
    order = relationship("Order", back_populates="items", passive_deletes=True)

    def __repr__(self):
        return (f"<Registration(id={self.id}, fullName={self.fullName}, "
                f"phone={self.phone}, status={self.status})>")
