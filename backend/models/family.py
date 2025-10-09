"""Family/guardian relationship models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.core.database import Base


class FamilyLink(Base):
    """Association table linking a guardian/parent account to a child account."""

    __tablename__ = "family_links"
    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "child_id",
            name="uq_family_link_parent_child",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_label = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship(
        "User",
        foreign_keys=[parent_id],
        back_populates="children_links",
    )
    child = relationship(
        "User",
        foreign_keys=[child_id],
        back_populates="guardian_links",
    )


__all__ = ["FamilyLink"]

