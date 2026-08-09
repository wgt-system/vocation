from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.availability import AvailabilityEvaluator, AvailabilityObservation
from vocation.infrastructure.models import (
    AvailabilityObservationModel,
    CompanyModel,
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    ResearchImportModel,
    SourceModel,
    SourceReferenceModel,
    WorkLocationModel,
)
from vocation.infrastructure.personal_triage_repository import SqlAlchemyPersonalTriageRepository


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).isoformat().replace("+00:00", "Z")


class SqlAlchemyOpportunityReadRepository:
    def __init__(self, session_factory: Callable[[], Session], clock: Callable[[], datetime] | None = None):
        self.session_factory = session_factory
        self.triage = SqlAlchemyPersonalTriageRepository(session_factory)
        self.clock = clock or (lambda: datetime.now(UTC))

    @staticmethod
    def _availability_observation(model: AvailabilityObservationModel) -> AvailabilityObservation:
        return AvailabilityObservation(
            model.id,
            model.posting_id,
            cast(Any, model.result),
            model.observed_at,
            model.recorded_at,
            model.evidence_summary,
        )

    def _availability(self, session: Session, posting_ids: list[str], now: datetime) -> dict[str, dict[str, Any]]:
        rows = session.scalars(
            select(AvailabilityObservationModel)
            .where(AvailabilityObservationModel.posting_id.in_(posting_ids))
            .order_by(
                AvailabilityObservationModel.observed_at.desc(),
                AvailabilityObservationModel.recorded_at.desc(),
                AvailabilityObservationModel.id.desc(),
            )
        ).all()
        grouped: dict[str, list[AvailabilityObservation]] = {}
        for row in rows:
            grouped.setdefault(row.posting_id, []).append(self._availability_observation(row))
        evaluator = AvailabilityEvaluator()
        return {
            posting_id: {
                "assessment": evaluator.posting(tuple(grouped.get(posting_id, [])), now),
                "history": [
                    {
                        "id": row.id,
                        "import_id": row.import_id,
                        "result": row.result,
                        "observed_at": _iso(row.observed_at),
                        "recorded_at": _iso(row.recorded_at),
                        "evidence_summary": row.evidence_summary,
                    }
                    for row in rows_for_posting
                ],
            }
            for posting_id, rows_for_posting in (
                (posting_id, [row for row in rows if row.posting_id == posting_id]) for posting_id in posting_ids
            )
        }

    def list(self) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            now = self.clock()
            opportunities = session.scalars(select(OpportunityModel).order_by(OpportunityModel.canonical_title)).all()
            result: list[dict[str, Any]] = []
            for opportunity in opportunities:
                company = session.get(CompanyModel, opportunity.company_id)
                locations = session.scalars(select(WorkLocationModel).where(WorkLocationModel.opportunity_id == opportunity.id)).all()
                postings = session.scalars(select(PostingModel).where(PostingModel.opportunity_id == opportunity.id)).all()
                assessments = session.scalars(
                    select(ExternalAssessmentModel).where(
                        ExternalAssessmentModel.subject_type == "opportunity",
                        ExternalAssessmentModel.subject_id == opportunity.id,
                    )
                ).all()
                aggregate = AvailabilityEvaluator().opportunity(
                    tuple(
                        tuple(
                            self._availability_observation(row)
                            for row in session.scalars(
                                select(AvailabilityObservationModel).where(AvailabilityObservationModel.posting_id == posting.id)
                            ).all()
                        )
                        for posting in postings
                    ),
                    now,
                )
                imported = session.get(ResearchImportModel, opportunity.import_id)
                result.append(
                    {
                        "id": opportunity.id,
                        "title": opportunity.canonical_title,
                        "company_name": company.canonical_name,
                        "locations": [location.label for location in locations],
                        "posting_count": len(postings),
                        "assessment_count": len(assessments),
                        "tracking_status": opportunity.tracking_status,
                        "import_id": opportunity.import_id,
                        "imported_at": _iso(imported.applied_at),
                        "availability": aggregate.availability,
                        "availability_last_checked_at": _iso(aggregate.last_checked_at),
                        "availability_age_days": aggregate.age_days,
                    }
                )
            return result

    def detail(self, opportunity_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            now = self.clock()
            opportunity = session.get(OpportunityModel, opportunity_id)
            if opportunity is None:
                return None
            company = session.get(CompanyModel, opportunity.company_id)
            locations = session.scalars(select(WorkLocationModel).where(WorkLocationModel.opportunity_id == opportunity.id)).all()
            postings = session.scalars(
                select(PostingModel).where(PostingModel.opportunity_id == opportunity.id).order_by(PostingModel.observed_at.desc())
            ).all()
            posting_details: list[dict[str, Any]] = []
            availability_by_posting = self._availability(session, [posting.id for posting in postings], now)
            source_details: dict[str, dict[str, Any]] = {}
            for posting in postings:
                reference = session.get(SourceReferenceModel, posting.source_reference_id)
                source = session.get(SourceModel, reference.source_id)
                source_details[source.id] = {
                    "id": source.id,
                    "name": source.name,
                    "type": source.source_type,
                    "base_url": source.base_url,
                }
                posting_details.append(
                    {
                        "id": posting.id,
                        "title": posting.title,
                        "external_posting_id": posting.external_posting_id,
                        "published_at": posting.published_at,
                        "observed_at": _iso(posting.observed_at),
                        "source": {
                            "id": source.id,
                            "name": source.name,
                            "type": source.source_type,
                        },
                        "source_reference": {
                            "id": reference.id,
                            "url": reference.url,
                            "display_label": reference.display_label,
                            "observed_at": _iso(reference.observed_at),
                        },
                        "availability": availability_by_posting[posting.id]["assessment"].availability,
                        "availability_last_checked_at": _iso(availability_by_posting[posting.id]["assessment"].last_checked_at),
                        "availability_age_days": availability_by_posting[posting.id]["assessment"].age_days,
                        "availability_history": availability_by_posting[posting.id]["history"],
                    }
                )
            subject_ids = [company.id, opportunity.id, *[posting.id for posting in postings]]
            observations = session.scalars(
                select(ObservationModel).where(ObservationModel.subject_id.in_(subject_ids)).order_by(ObservationModel.observed_at.desc())
            ).all()
            assessments = session.scalars(
                select(ExternalAssessmentModel)
                .where(ExternalAssessmentModel.subject_id.in_(subject_ids))
                .order_by(ExternalAssessmentModel.created_at.desc())
            ).all()
            imported = session.get(ResearchImportModel, opportunity.import_id)
            aggregate = AvailabilityEvaluator().opportunity(
                tuple(
                    tuple(
                        self._availability_observation(row)
                        for row in session.scalars(
                            select(AvailabilityObservationModel).where(AvailabilityObservationModel.posting_id == posting.id)
                        ).all()
                    )
                    for posting in postings
                ),
                now,
            )
            return {
                "id": opportunity.id,
                "title": opportunity.canonical_title,
                "company": {"id": company.id, "name": company.canonical_name},
                "locations": [
                    {
                        "label": location.label,
                        "city": location.city,
                        "region": location.region,
                        "country_code": location.country_code,
                        "precision": location.precision,
                        "observed_at": _iso(location.observed_at),
                        "evidence_summary": location.evidence_summary,
                    }
                    for location in locations
                ],
                "postings": posting_details,
                "sources": list(source_details.values()),
                "observations": [
                    {
                        "id": item.id,
                        "subject_type": item.subject_type,
                        "type": item.observation_type,
                        "value": json.loads(item.value_json),
                        "observed_at": _iso(item.observed_at),
                        "confidence": item.confidence,
                        "evidence_summary": item.evidence_summary,
                    }
                    for item in observations
                ],
                "external_assessments": [
                    {
                        "id": item.id,
                        "subject_type": item.subject_type,
                        "criterion_id": item.criterion_id,
                        "criterion_name": item.criterion.display_name,
                        "value": json.loads(item.value_json),
                        "origin": item.origin,
                        "created_at": _iso(item.created_at),
                        "reasoning": item.reasoning,
                    }
                    for item in assessments
                ],
                "assessments": [
                    {
                        "id": item.id,
                        "subject_type": item.subject_type,
                        "criterion_id": item.criterion_id,
                        "criterion_name": item.criterion.display_name,
                        "value": json.loads(item.value_json),
                        "origin": item.origin,
                        "created_at": _iso(item.created_at),
                        "reasoning": item.reasoning,
                    }
                    for item in assessments
                ],
                "tracking_status": opportunity.tracking_status,
                "personal_assessments": self.triage.current_assessments(opportunity.id),
                "personal_assessment_history": self.triage.assessment_history(opportunity.id),
                "decision_history": self.triage.decisions(opportunity.id),
                "import_provenance": {
                    "import_id": imported.id,
                    "bundle_id": imported.bundle_id,
                    "fingerprint": imported.fingerprint,
                    "applied_at": _iso(imported.applied_at),
                },
                "availability": aggregate.availability,
                "availability_last_checked_at": _iso(aggregate.last_checked_at),
                "availability_age_days": aggregate.age_days,
            }
