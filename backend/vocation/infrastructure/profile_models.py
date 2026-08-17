from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vocation.infrastructure.models import Base


class CandidateProfileRevisionModel(Base):
    __tablename__ = "candidate_profile_revisions"

    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SearchProfileModel(Base):
    __tablename__ = "search_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revisions: Mapped[list[SearchProfileRevisionModel]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="SearchProfileRevisionModel.revision",
    )


class SearchProfileRevisionModel(Base):
    __tablename__ = "search_profile_revisions"

    search_profile_id: Mapped[str] = mapped_column(
        ForeignKey("search_profiles.id", ondelete="CASCADE"), primary_key=True
    )
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    profile: Mapped[SearchProfileModel] = relationship(back_populates="revisions")
