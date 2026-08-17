from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from vocation.infrastructure.models import Base


class DuplicateCaseDecisionModel(Base):
    __tablename__ = "duplicate_case_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    duplicate_case_id: Mapped[str] = mapped_column(ForeignKey("duplicate_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "duplicate_case_id",
            "sequence",
            name="uq_duplicate_case_decisions_sequence",
        ),
        CheckConstraint("sequence >= 1", name="ck_duplicate_case_decisions_sequence"),
        CheckConstraint(
            "outcome IN ('confirmed_duplicate','confirmed_distinct','related_but_distinct','keep_unresolved')",
            name="ck_duplicate_case_decisions_outcome",
        ),
        CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_duplicate_case_decisions_reason_nonempty",
        ),
    )
