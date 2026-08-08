from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.personal_triage import PersonalTriageConflictError
from vocation.infrastructure.models import OpportunityDecisionModel, OpportunityModel, PersonalAssessmentModel


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


class SqlAlchemyPersonalTriageRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def assessment_history(self, opportunity_id: str) -> list[dict]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(PersonalAssessmentModel)
                .where(PersonalAssessmentModel.opportunity_id == opportunity_id)
                .order_by(PersonalAssessmentModel.criterion_id, PersonalAssessmentModel.revision_number)
            ).all()
            return [self._assessment(row) for row in rows]

    def current_assessments(self, opportunity_id: str) -> list[dict]:
        history = self.assessment_history(opportunity_id)
        current: dict[str, dict] = {}
        for item in history:
            current[item["criterion_id"]] = item
        return list(current.values())

    def create_assessment(self, opportunity_id: str, criterion_id: str, value: object, reasoning: str | None) -> dict:
        with self.session_factory.begin() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                raise LookupError(opportunity_id)
            previous = session.scalars(select(PersonalAssessmentModel).where(
                PersonalAssessmentModel.opportunity_id == opportunity_id,
                PersonalAssessmentModel.criterion_id == criterion_id,
            )).first()
            if previous is not None:
                raise PersonalTriageConflictError("A personal assessment already exists for this opportunity and criterion.")
            row = PersonalAssessmentModel(
                id=str(uuid4()),
                opportunity_id=opportunity_id,
                criterion_id=criterion_id,
                value_json=json.dumps(value, ensure_ascii=False),
                reasoning=reasoning,
                created_at=datetime.now(UTC),
                supersedes_id=None,
                revision_number=1,
                origin="personal",
            )
            session.add(row)
        result = self.get_assessment(row.id)
        assert result is not None
        return result

    def revise_assessment(self, opportunity_id: str, assessment_id: str, value: object, reasoning: str | None) -> dict:
        with self.session_factory.begin() as session:
            previous = session.get(PersonalAssessmentModel, assessment_id)
            if previous is None or previous.opportunity_id != opportunity_id:
                raise LookupError(assessment_id)
            latest = session.scalars(
                select(PersonalAssessmentModel)
                .where(
                    PersonalAssessmentModel.opportunity_id == opportunity_id,
                    PersonalAssessmentModel.criterion_id == previous.criterion_id,
                )
                .order_by(PersonalAssessmentModel.revision_number.desc())
            ).first()
            if latest is None or latest.id != previous.id:
                raise PersonalTriageConflictError("Only the current personal assessment can be revised.")
            row = PersonalAssessmentModel(
                id=str(uuid4()),
                opportunity_id=opportunity_id,
                criterion_id=previous.criterion_id,
                value_json=json.dumps(value, ensure_ascii=False),
                reasoning=reasoning,
                created_at=datetime.now(UTC),
                supersedes_id=previous.id,
                revision_number=previous.revision_number + 1,
                origin="personal",
            )
            session.add(row)
        result = self.get_assessment(row.id)
        assert result is not None
        return result

    def get_assessment(self, assessment_id: str) -> dict | None:
        with self.session_factory() as session:
            row = session.get(PersonalAssessmentModel, assessment_id)
            return self._assessment(row) if row else None

    def status(self, opportunity_id: str) -> str:
        with self.session_factory() as session:
            row = session.get(OpportunityModel, opportunity_id)
            if row is None:
                raise LookupError(opportunity_id)
            return row.tracking_status

    def decide(
        self, opportunity_id: str, resulting_status: str, decision_type: str, reason: str | None, reverses: str | None = None
    ) -> dict:
        with self.session_factory.begin() as session:
            opportunity = session.get(OpportunityModel, opportunity_id)
            if opportunity is None:
                raise LookupError(opportunity_id)
            row = OpportunityDecisionModel(
                id=str(uuid4()),
                opportunity_id=opportunity_id,
                decision_type=decision_type,
                previous_status=opportunity.tracking_status,
                resulting_status=resulting_status,
                reason=reason,
                created_at=datetime.now(UTC),
                reverses_decision_id=reverses,
            )
            opportunity.tracking_status = resulting_status
            session.add(row)
        return self._decision(row)

    def decisions(self, opportunity_id: str) -> list[dict]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(OpportunityDecisionModel)
                .where(OpportunityDecisionModel.opportunity_id == opportunity_id)
                .order_by(OpportunityDecisionModel.created_at, OpportunityDecisionModel.id)
            ).all()
            return [self._decision(row) for row in rows]

    def active_exclusion(self, opportunity_id: str) -> dict | None:
        with self.session_factory() as session:
            decisions = session.scalars(
                select(OpportunityDecisionModel)
                .where(OpportunityDecisionModel.opportunity_id == opportunity_id)
                .order_by(OpportunityDecisionModel.created_at, OpportunityDecisionModel.id)
            ).all()
            restored_ids = {item.reverses_decision_id for item in decisions if item.decision_type == "restore"}
            for item in reversed(decisions):
                if item.decision_type == "exclusion" and item.resulting_status == "excluded" and item.id not in restored_ids:
                    return self._decision(item)
            return None

    @staticmethod
    def _assessment(row: PersonalAssessmentModel) -> dict:
        return {
            "id": row.id,
            "opportunity_id": row.opportunity_id,
            "criterion_id": row.criterion_id,
            "criterion_name": row.criterion.display_name,
            "value": json.loads(row.value_json),
            "reasoning": row.reasoning,
            "created_at": _iso(row.created_at),
            "supersedes_id": row.supersedes_id,
            "revision_number": row.revision_number,
            "origin": row.origin,
        }

    @staticmethod
    def _decision(row: OpportunityDecisionModel) -> dict:
        return {
            "id": row.id,
            "opportunity_id": row.opportunity_id,
            "decision_type": row.decision_type,
            "previous_status": row.previous_status,
            "resulting_status": row.resulting_status,
            "reason": row.reason,
            "created_at": _iso(row.created_at),
            "reverses_decision_id": row.reverses_decision_id,
        }
