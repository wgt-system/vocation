from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.infrastructure.models import (
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
    return value.isoformat().replace("+00:00", "Z") if value else None


class SqlAlchemyOpportunityReadRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory
        self.triage = SqlAlchemyPersonalTriageRepository(session_factory)

    def list(self) -> list[dict[str, Any]]:
        with self.session_factory() as session:
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
                    }
                )
            return result

    def detail(self, opportunity_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            opportunity = session.get(OpportunityModel, opportunity_id)
            if opportunity is None:
                return None
            company = session.get(CompanyModel, opportunity.company_id)
            locations = session.scalars(select(WorkLocationModel).where(WorkLocationModel.opportunity_id == opportunity.id)).all()
            postings = session.scalars(
                select(PostingModel).where(PostingModel.opportunity_id == opportunity.id).order_by(PostingModel.observed_at.desc())
            ).all()
            posting_details: list[dict[str, Any]] = []
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
            }
