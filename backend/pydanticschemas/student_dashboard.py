"""Pydantic schemas powering the student dashboard API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from backend.pydanticschemas.learning_paths import LearningPathProgress


class StudentCourseProgress(BaseModel):
    """Detailed view of a learner's progress for a single registration."""

    registration_id: int
    course_id: Optional[int]
    course_title: Optional[str]
    course_summary: Optional[str]
    course_image_url: Optional[str]
    course_price: Optional[float]
    status: str
    registered_at: datetime
    order_id: Optional[int]
    order_status: Optional[str]
    payment_status: Optional[str]
    outstanding_balance: float
    progress: LearningPathProgress

    class Config:
        from_attributes = True


class StudentDashboardResponse(BaseModel):
    """Aggregate payload returned by the student dashboard endpoint."""

    student_id: int
    student_email: EmailStr
    display_name: Optional[str]
    total_courses: int
    active_courses: int
    completed_courses: int
    latest_activity_at: Optional[datetime]
    courses: List[StudentCourseProgress]
