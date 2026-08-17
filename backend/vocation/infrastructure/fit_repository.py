from __future__ import annotations

import json
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.fit import AssessmentEvidence
from vocation.infrastructure.models import ExternalAssessmentModel, OpportunityModel, PersonalAssessmentModel


class SqlAlchemyFitRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def opportunity_exists(self, opportunity_id: str) -> bool:
        with self.session_factory() as session:
            return session.get(OpportunityModel, opportunity_id) is not None

    def opportunity_ids(self) -> list[str]:
        with self.session_factory() as session:
            return list(session.scalars(select(OpportunityModel.id).order_by(OpportunityModel.id)).all())

    def effective_assessments(self, opportunity_id: str) -> dict[str, AssessmentEvidence]:
        with self.session_factory() as session:
            external_rows = session.scalars(
                select(ExternalAssessmentModel)
                .where(
                    ExternalAssessmentModel.subject_type == "opportunity",
                    ExternalAssessmentModel.subject_id == opportunity_id,
                )
                .order_by(ExternalAssessmentModel.created_at, ExternalAssessmentModel.id)
            ).all()
            personal_rows = session.scalars(
                select(PersonalAssessmentModel)
                .where(PersonalAssessmentModel.opportunity_id == opportunity_id)
                .order_by(PersonalAssessmentModel.criterion_id, PersonalAssessmentModel.revision_number)
            ).all()

        effective: dict[str, AssessmentEvidence] = {}
        for row in external_rows:
            effective[row.criterion_id] = AssessmentEvidence(
                criterion_id=row.criterion_id,
                value=json.loads(row.value_json),
                origin=row.origin,
                reasoning=row.reasoning,
            )
        for row in personal_rows:
            effective[row.criterion_id] = AssessmentEvidence(
                criterion_id=row.criterion_id,
                value=json.loads(row.value_json),
                origin=row.origin,
                reasoning=row.reasoning,
            )
        return effective
