from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.availability import AvailabilityEvaluator, AvailabilityObservation
from vocation.domain.external_links import ExternalLink, SourceType
from vocation.infrastructure.models import (
    AvailabilityObservationModel,
    OpportunityModel,
    PostingModel,
    SourceModel,
    SourceReferenceModel,
)


class SqlAlchemyExternalLinkRepository:
    def __init__(self, session_factory: Callable[[], Session], clock: Callable[[], datetime] | None = None):
        self.session_factory = session_factory
        self.clock = clock or (lambda: datetime.now(UTC))

    def links_for_opportunity(self, opportunity_id: str) -> list[ExternalLink] | None:
        with self.session_factory() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                return None
            postings = session.scalars(
                select(PostingModel)
                .where(PostingModel.opportunity_id == opportunity_id)
                .order_by(PostingModel.observed_at.desc(), PostingModel.id.asc())
            ).all()
            return [self._link(session, posting) for posting in postings]

    def links_for_posting(self, opportunity_id: str, posting_id: str) -> list[ExternalLink] | None:
        with self.session_factory() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                return None
            posting = session.get(PostingModel, posting_id)
            if posting is None or posting.opportunity_id != opportunity_id:
                return None
            return [self._link(session, posting)]

    def _link(self, session: Session, posting: PostingModel) -> ExternalLink:
        reference = session.get(SourceReferenceModel, posting.source_reference_id)
        source = session.get(SourceModel, reference.source_id)
        rows = session.scalars(select(AvailabilityObservationModel).where(AvailabilityObservationModel.posting_id == posting.id)).all()
        observations = tuple(
            AvailabilityObservation(
                row.id,
                row.posting_id,
                cast(object, row.result),  # type: ignore[arg-type]
                row.observed_at,
                row.recorded_at,
                row.evidence_summary,
            )
            for row in rows
        )
        availability = AvailabilityEvaluator().posting(observations, self.clock()).availability
        return ExternalLink(
            posting_id=posting.id,
            source_id=source.id,
            source_name=source.name,
            source_type=cast(SourceType, source.source_type),
            url=reference.url,
            display_label=reference.display_label,
            availability=availability,
            observed_at=posting.observed_at,
        )
