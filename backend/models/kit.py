from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Kit(Base):
    __tablename__ = "kits"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    thumbnail_url = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    sections = relationship(
        "KitSection",
        back_populates="kit",
        cascade="all, delete-orphan",
        order_by="KitSection.position",
    )

    def __repr__(self) -> str:
        return f"<Kit(id={self.id}, title={self.title}, status={self.status})>"


class KitSection(Base):
    __tablename__ = "kit_sections"

    id = Column(Integer, primary_key=True, index=True)
    kit_id = Column(Integer, ForeignKey("kits.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    kit = relationship("Kit", back_populates="sections")
    assets = relationship(
        "KitAsset",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="KitAsset.id",
    )

    def __repr__(self) -> str:
        return f"<KitSection(id={self.id}, kit_id={self.kit_id}, name={self.name})>"


class KitAsset(Base):
    __tablename__ = "kit_assets"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("kit_sections.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=True)
    label = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("KitSection", back_populates="assets")

    def __repr__(self) -> str:
        return f"<KitAsset(id={self.id}, label={self.label}, file_url={self.file_url})>"
