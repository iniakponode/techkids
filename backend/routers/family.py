"""Endpoints for managing guardian/child relationships."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.dependencies.auth_roles import require_role
from backend.models.family import FamilyLink
from backend.models.user import User
from backend.pydanticschemas.family import (
    FamilyOverviewResponse,
    LinkChildRequest,
    LinkedChildResponse,
)
from backend.services.family import build_child_response


router = APIRouter(prefix="/family", tags=["family"])


def _get_parent_user(current_user: User) -> User:
    if current_user.role not in {"parent", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents or admins can manage family links.",
        )
    return current_user


@router.get("/children", response_model=FamilyOverviewResponse)
def list_linked_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["parent", "admin"])),
):
    """Return the guardian's currently linked children."""

    parent = _get_parent_user(current_user)

    links = (
        db.query(FamilyLink)
        .filter(FamilyLink.parent_id == parent.id)
        .order_by(FamilyLink.created_at.asc())
        .all()
    )

    children = [build_child_response(db, link) for link in links]

    return FamilyOverviewResponse(
        parent_id=parent.id,
        parent_email=parent.email,
        children=children,
    )


@router.post("/children", response_model=LinkedChildResponse, status_code=status.HTTP_201_CREATED)
def link_child(
    payload: LinkChildRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["parent", "admin"])),
):
    """Link an existing child account to the authenticated guardian."""

    parent = _get_parent_user(current_user)

    child = db.query(User).filter(User.email == payload.child_email).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for the provided child email.",
        )

    if child.id == parent.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot link your own account as a child.",
        )

    if child.role not in {"student", "child"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only learner accounts can be linked as children.",
        )

    existing = (
        db.query(FamilyLink)
        .filter(
            FamilyLink.parent_id == parent.id,
            FamilyLink.child_id == child.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This child is already linked to your account.",
        )

    link = FamilyLink(
        parent_id=parent.id,
        child_id=child.id,
        relationship=payload.relationship,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return build_child_response(db, link)


@router.get("/children/{child_id}", response_model=LinkedChildResponse)
def get_child_details(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["parent", "admin"])),
):
    """Fetch details for a specific linked child."""

    parent = _get_parent_user(current_user)

    link = (
        db.query(FamilyLink)
        .filter(
            FamilyLink.parent_id == parent.id,
            FamilyLink.child_id == child_id,
        )
        .first()
    )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not linked to this guardian.",
        )

    return build_child_response(db, link)


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["parent", "admin"])),
):
    """Remove a child link from the guardian account."""

    parent = _get_parent_user(current_user)

    deleted = (
        db.query(FamilyLink)
        .filter(
            FamilyLink.parent_id == parent.id,
            FamilyLink.child_id == child_id,
        )
        .delete()
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not linked to this guardian.",
        )

    db.commit()

