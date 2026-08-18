from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from vocation.infrastructure.models import Base


class SearchVocabularyEntryModel(Base):
    __tablename__ = "search_vocabulary_entries"
    __table_args__ = (UniqueConstraint("kind", "normalized_label", name="uq_search_vocabulary_kind_label"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    normalized_label: Mapped[str] = mapped_column(String(160), nullable=False)
    aliases_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    group_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
