from __future__ import annotations

from vocation.domain.criteria import AssessmentCriterion, validate_assessment_value
from vocation.domain.personal_triage import (
    PersonalTriageError,
    validate_exclusion_reason,
    validate_restore_target,
    validate_tracking_status,
)


class PersonalTriageService:
    def __init__(self, repository, criteria_repository):
        self.repository = repository
        self.criteria_repository = criteria_repository

    def _criterion(self, criterion_id: str) -> AssessmentCriterion:
        criterion = self.criteria_repository.get(criterion_id)
        if criterion is None:
            raise LookupError(criterion_id)
        return criterion

    def _validate(self, criterion_id: str, value: object) -> None:
        criterion = self._criterion(criterion_id)
        if not criterion.active:
            raise PersonalTriageError("Only active assessment criteria can receive a new personal assessment.")
        if criterion.applicable_subject_type != "opportunity" or not validate_assessment_value(criterion, value):
            raise PersonalTriageError(f"Value is invalid for criterion '{criterion_id}'.")

    def create_assessment(self, opportunity_id: str, criterion_id: str, value: object, reasoning: str | None) -> dict:
        self._validate(criterion_id, value)
        return self.repository.create_assessment(opportunity_id, criterion_id, value, reasoning)

    def revise_assessment(self, opportunity_id: str, assessment_id: str, value: object, reasoning: str | None) -> dict:
        with self.repository.session_factory() as session:
            from vocation.infrastructure.models import PersonalAssessmentModel

            row = session.get(PersonalAssessmentModel, assessment_id)
            if row is None or row.opportunity_id != opportunity_id:
                raise LookupError(assessment_id)
            criterion_id = row.criterion_id
        self._validate(criterion_id, value)
        return self.repository.revise_assessment(opportunity_id, assessment_id, value, reasoning)

    def change_status(self, opportunity_id: str, status: str, reason: str | None = None) -> dict:
        validate_tracking_status(status)
        current = self.repository.status(opportunity_id)
        if current == "excluded" and status != "excluded":
            raise PersonalTriageError("Excluded opportunities must be restored explicitly.")
        if current == status:
            raise PersonalTriageError("Tracking status is unchanged.")
        return self.repository.decide(opportunity_id, status, "status_change", reason)

    def exclude(self, opportunity_id: str, reason: str) -> dict:
        reason = validate_exclusion_reason(reason)
        current = self.repository.status(opportunity_id)
        if current == "excluded":
            raise PersonalTriageError("Opportunity is already excluded.")
        return self.repository.decide(opportunity_id, "excluded", "exclusion", reason)

    def restore(self, opportunity_id: str, target_status: str | None, reason: str | None) -> dict:
        target = validate_restore_target(target_status)
        current = self.repository.status(opportunity_id)
        if current != "excluded":
            raise PersonalTriageError("Only excluded opportunities can be restored.")
        decisions = self.repository.decisions(opportunity_id)
        exclusion = next((item for item in reversed(decisions) if item["resulting_status"] == "excluded"), None)
        return self.repository.decide(opportunity_id, target, "restore", reason, exclusion["id"] if exclusion else None)
