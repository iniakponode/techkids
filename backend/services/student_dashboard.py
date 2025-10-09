"""Service helpers for assembling the student dashboard payload."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from backend.models.registration import Registration
from backend.models.user import User
from backend.pydanticschemas.student_dashboard import (
    StudentCourseProgress,
    StudentDashboardResponse,
)
from backend.services.learning_paths import build_learning_path_progress


_PAID_ORDER_STATUSES = {"paid", "completed"}
_SUCCESSFUL_PAYMENT_STATUSES = {"successful", "paid", "completed"}


def _derive_display_name(student: User, registrations: List[Registration]) -> Optional[str]:
    """Return a friendly name for the learner when possible."""

    for reg in registrations:
        full_name = (reg.fullName or "").strip()
        if full_name:
            return full_name

    local_part = student.email.split("@", 1)[0]
    if not local_part:
        return None
    return local_part.replace(".", " ").title()


def _financial_snapshot(registration: Registration) -> Tuple[float, Optional[int], Optional[str], Optional[str]]:
    """Compute the outstanding balance and payment details for a registration."""

    order = registration.order
    course = registration.course

    course_price = course.price if course else None
    if course_price in (None, 0):
        return (
            0.0,
            order.id if order else None,
            order.status if order else None,
            order.payment.status if order and order.payment else None,
        )

    outstanding = 0.0
    order_status = order.status if order else None
    payment_status = order.payment.status if order and order.payment else None

    registration_state = (registration.status or "").lower()

    if not order:
        if registration_state not in {"cancelled", "completed"}:
            outstanding = course_price
    else:
        payment_state = (payment_status or "").lower() if payment_status is not None else None
        if payment_state is not None:
            if payment_state not in _SUCCESSFUL_PAYMENT_STATUSES:
                outstanding = course_price
        else:
            order_state = (order_status or "").lower() if order_status is not None else None
            if order_state not in _PAID_ORDER_STATUSES:
                outstanding = course_price

    return (
        round(outstanding, 2),
        order.id if order else None,
        order_status,
        payment_status,
    )


def build_student_dashboard(db: Session, student: User) -> StudentDashboardResponse:
    """Compile the student's dashboard overview and per-course progress."""

    registrations: List[Registration] = (
        db.query(Registration)
        .filter(Registration.user_id == student.id)
        .order_by(Registration.registered_at.asc())
        .all()
    )

    display_name = _derive_display_name(student, registrations)

    courses: List[StudentCourseProgress] = []
    latest_activity: Optional[datetime] = None
    completed_courses = 0
    active_courses = 0

    for registration in registrations:
        progress_payload = build_learning_path_progress(db, registration)

        if progress_payload.last_activity_at and (
            latest_activity is None or progress_payload.last_activity_at > latest_activity
        ):
            latest_activity = progress_payload.last_activity_at

        completion_percentage = progress_payload.completion_percentage or 0.0
        registration_state = (registration.status or "").lower()

        if completion_percentage >= 99.999 or registration_state == "completed":
            completed_courses += 1
        elif registration_state not in {"cancelled"}:
            active_courses += 1

        outstanding_balance, order_id, order_status, payment_status = _financial_snapshot(
            registration
        )

        course = registration.course

        courses.append(
            StudentCourseProgress(
                registration_id=registration.id,
                course_id=registration.course_id,
                course_title=course.title if course else None,
                course_summary=course.summary if course else None,
                course_image_url=course.image_url if course else None,
                course_price=course.price if course else None,
                status=registration.status,
                registered_at=registration.registered_at,
                order_id=order_id,
                order_status=order_status,
                payment_status=payment_status,
                outstanding_balance=outstanding_balance,
                progress=progress_payload,
            )
        )

    total_courses = len(registrations)

    return StudentDashboardResponse(
        student_id=student.id,
        student_email=student.email,
        display_name=display_name,
        total_courses=total_courses,
        active_courses=active_courses,
        completed_courses=completed_courses,
        latest_activity_at=latest_activity,
        courses=courses,
    )
