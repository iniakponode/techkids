"""Helper utilities for guardian/child data aggregation."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from backend.models.family import FamilyLink
from backend.models.registration import Registration
from backend.pydanticschemas.family import (
    ChildRegistrationSummary,
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
        if reg.order and reg.order.payment:
            payment_status = reg.order.payment.status

        if not display_name and reg.fullName:
            display_name = reg.fullName

        reg_status_value = (reg.status or "").lower()
        should_count_outstanding = False
        if course_price:
            if not reg.order:
                should_count_outstanding = reg_status_value not in {"cancelled", "completed"}
            else:
                if reg.order.payment:
                    payment_status_value = (reg.order.payment.status or "").lower()
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

