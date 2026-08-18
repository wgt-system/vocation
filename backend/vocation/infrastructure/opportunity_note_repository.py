from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from vocation.infrastructure.models import Base, OpportunityModel


class OpportunityNoteModel(Base):
    __tablename__ = "opportunity_notes"

    opportunity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class SqlAlchemyOpportunityNoteRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, opportunity_id: str) -> dict | None:
        with self.session_factory() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                raise LookupError(opportunity_id)
            row = session.get(OpportunityNoteModel, opportunity_id)
            return self._note(row) if row is not None else None

    def save(self, opportunity_id: str, content: str) -> dict:
        now = datetime.now(UTC)
        with self.session_factory.begin() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                raise LookupError(opportunity_id)
            row = session.get(OpportunityNoteModel, opportunity_id)
            if row is None:
                row = OpportunityNoteModel(
                    opportunity_id=opportunity_id,
                    content=content,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.content = content
                row.updated_at = now
        return {
            "opportunity_id": opportunity_id,
            "content": content,
            "updated_at": _iso(now),
        }

    def clear(self, opportunity_id: str) -> None:
        with self.session_factory.begin() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                raise LookupError(opportunity_id)
            row = session.get(OpportunityNoteModel, opportunity_id)
            if row is not None:
                session.delete(row)

    @staticmethod
    def _note(row: OpportunityNoteModel) -> dict:
        return {
            "opportunity_id": row.opportunity_id,
            "content": row.content,
            "updated_at": _iso(row.updated_at),
        }
