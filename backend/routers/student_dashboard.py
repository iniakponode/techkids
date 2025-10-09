"""Endpoints powering the student-facing dashboard experience."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.dependencies.auth_roles import require_role
from backend.models.user import User
from backend.pydanticschemas.student_dashboard import StudentDashboardResponse
from backend.services.student_dashboard import build_student_dashboard


router = APIRouter(prefix="/students", tags=["students"])


@router.get("/dashboard", response_model=StudentDashboardResponse)
def get_student_dashboard(
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["student", "child", "admin"])),
) -> StudentDashboardResponse:
    """Return the authenticated learner's dashboard, or a specified learner for admins."""

    if current_user.role == "admin":
        if student_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required to view another learner's dashboard.",
            )

        student = db.query(User).filter(User.id == student_id).first()
        if not student or student.role not in {"student", "child"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found.",
            )
    else:
        if student_id is not None and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own dashboard.",
            )
        student = current_user

    return build_student_dashboard(db, student)
