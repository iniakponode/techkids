"""Helper utilities for guardian/child data aggregation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.family import FamilyLink
from backend.models.registration import Registration
from backend.pydanticschemas.family import (
    ChildRegistrationSummary,
    LearningProgressSummary,
    LinkedChildResponse,
)


def _derive_display_name(existing: Optional[str], child_email: str) -> Optional[str]:
    """Return a sensible display name for the child."""

    if existing:
        return existing

    local_part = child_email.split("@", 1)[0]
    if not local_part:
        return None
    return local_part.replace(".", " ").title()


def build_child_response(db: Session, link: FamilyLink) -> LinkedChildResponse:
    """Assemble a ``LinkedChildResponse`` from a ``FamilyLink`` instance."""

    child = link.child

    registrations: list[Registration] = (
        db.query(Registration)
        .filter(Registration.user_id == child.id)
        .all()
    )

    reg_summaries: list[ChildRegistrationSummary] = []
    outstanding = 0.0
    display_name: Optional[str] = None

    for reg in registrations:
        course_title = reg.course.title if reg.course else None
        course_price = reg.course.price if reg.course else None
        order_status = reg.order.status if reg.order else None
        payment_status = None
        payment_status_value = None
        payment_obj = None
        if reg.order:
            raw_payment = getattr(reg.order, "payment", None)
            if isinstance(raw_payment, Iterable) and not isinstance(raw_payment, (str, bytes)):
                for candidate in raw_payment:
                    if candidate is not None:
                        payment_obj = candidate
            else:
                payment_obj = raw_payment

        if payment_obj:
            payment_status = payment_obj.status
            payment_status_value = (payment_status or "").lower()

        if not display_name and reg.fullName:
            display_name = reg.fullName

        progress_summary: Optional[LearningProgressSummary] = None
        if reg.progress:
            raw_percentage = reg.progress.completion_percentage or 0.0
            calculated_percentage = raw_percentage
            if reg.progress.total_lessons:
                calculated_percentage = (
                    reg.progress.completed_lessons / reg.progress.total_lessons
                ) * 100

            progress_summary = LearningProgressSummary(
                completed_lessons=reg.progress.completed_lessons,
                total_lessons=reg.progress.total_lessons,
                completion_percentage=round(calculated_percentage, 2),
                current_module=reg.progress.current_module,
                current_lesson=reg.progress.current_lesson,
                last_activity_at=reg.progress.last_activity_at,
            )

        reg_status_value = (reg.status or "").lower()
        should_count_outstanding = False
        if course_price:
            if not reg.order:
                should_count_outstanding = reg_status_value not in {"cancelled", "completed"}
            else:
                if payment_status_value is not None:
                    if payment_status_value not in {"successful", "paid", "completed"}:
                        should_count_outstanding = True
                else:
                    order_status_value = (order_status or "").lower()
                    if order_status_value not in {"paid", "completed"}:
                        should_count_outstanding = True

        if should_count_outstanding and course_price:
            outstanding += course_price

        reg_summaries.append(
            ChildRegistrationSummary(
                registration_id=reg.id,
                course_id=reg.course_id,
                course_title=course_title,
                course_price=course_price,
                status=reg.status,
                order_id=reg.order_id,
                order_status=order_status,
                payment_status=payment_status,
                progress=progress_summary,
            )
        )

    display_name = _derive_display_name(display_name, child.email)

    return LinkedChildResponse(
        id=child.id,
        email=child.email,
        role=child.role,
        relationship_label=link.relationship_label,
        linked_at=link.created_at,
        display_name=display_name,
        registrations=reg_summaries,
        outstanding_balance=round(outstanding, 2),
    )

