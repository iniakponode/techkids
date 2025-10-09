"""Pydantic schemas for family/guardian management."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class LinkChildRequest(BaseModel):
    """Request payload for linking an existing child account to a guardian."""

    child_email: EmailStr
    relationship_label: Optional[str] = None


class LearningProgressSummary(BaseModel):
    completed_lessons: int
    total_lessons: int
    completion_percentage: float
    current_module: Optional[str]
    current_lesson: Optional[str]
    last_activity_at: Optional[datetime]


class ChildRegistrationSummary(BaseModel):
    registration_id: int
    course_id: Optional[int]
    course_title: Optional[str]
    course_price: Optional[float]
    status: str
    order_id: Optional[int]
    order_status: Optional[str]
    payment_status: Optional[str]
    progress: Optional[LearningProgressSummary]


class LinkedChildResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    relationship_label: Optional[str]
    linked_at: datetime
    display_name: Optional[str]
    registrations: List[ChildRegistrationSummary]
    outstanding_balance: float

    class Config:
        from_attributes = True


class FamilyOverviewResponse(BaseModel):
    parent_id: int
    parent_email: EmailStr
    children: List[LinkedChildResponse]

