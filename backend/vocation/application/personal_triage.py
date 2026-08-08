from __future__ import annotations

from vocation.application.ports import CriteriaRepository, PersonalTriageRepository
from vocation.domain.criteria import AssessmentCriterion
from vocation.domain.personal_triage import (
    PersonalTriageConflictError,
    PersonalTriageError,
    validate_exclusion_reason,
    validate_personal_assessment,
    validate_restore_target,
    validate_tracking_status,
)


class PersonalTriageService:
    def __init__(self, repository: PersonalTriageRepository, criteria_repository: CriteriaRepository):
        self.repository = repository
        self.criteria_repository = criteria_repository

    def _criterion(self, criterion_id: str) -> AssessmentCriterion:
        criterion = self.criteria_repository.get(criterion_id)
        if criterion is None:
            raise LookupError(criterion_id)
        return criterion

    def _validate(self, criterion_id: str, value: object) -> None:
        criterion = self._criterion(criterion_id)
        validate_personal_assessment(criterion, value)

    def create_assessment(self, opportunity_id: str, criterion_id: str, value: object, reasoning: str | None) -> dict:
        self._validate(criterion_id, value)
        return self.repository.create_assessment(opportunity_id, criterion_id, value, reasoning)

    def assessment_history(self, opportunity_id: str) -> list[dict]:
        self.repository.status(opportunity_id)
        return self.repository.assessment_history(opportunity_id)

    def current_assessments(self, opportunity_id: str) -> list[dict]:
        self.repository.status(opportunity_id)
        return self.repository.current_assessments(opportunity_id)

    def decisions(self, opportunity_id: str) -> list[dict]:
        self.repository.status(opportunity_id)
        return self.repository.decisions(opportunity_id)

    def revise_assessment(self, opportunity_id: str, assessment_id: str, value: object, reasoning: str | None) -> dict:
        assessment = self.repository.get_assessment(assessment_id)
        if assessment is None or assessment["opportunity_id"] != opportunity_id:
                raise LookupError(assessment_id)
        self._validate(assessment["criterion_id"], value)
        return self.repository.revise_assessment(opportunity_id, assessment_id, value, reasoning)

    def change_status(self, opportunity_id: str, status: str, reason: str | None = None) -> dict:
        validate_tracking_status(status)
        if status == "excluded":
            raise PersonalTriageError("Only ExcludeOpportunity can create the excluded status.")
        current = self.repository.status(opportunity_id)
        if current == "excluded" and status != "excluded":
            raise PersonalTriageConflictError("Excluded opportunities must be restored explicitly.")
        if current == status:
            raise PersonalTriageConflictError("Tracking status is unchanged.")
        return self.repository.decide(opportunity_id, status, "status_change", reason)

    def exclude(self, opportunity_id: str, reason: str) -> dict:
        reason = validate_exclusion_reason(reason)
        current = self.repository.status(opportunity_id)
        if current == "excluded":
            raise PersonalTriageConflictError("Opportunity is already excluded.")
        return self.repository.decide(opportunity_id, "excluded", "exclusion", reason)

    def restore(self, opportunity_id: str, target_status: str | None, reason: str | None) -> dict:
        current = self.repository.status(opportunity_id)
        if current != "excluded":
            raise PersonalTriageConflictError("Only excluded opportunities can be restored.")
        exclusion = self.repository.active_exclusion(opportunity_id)
        if exclusion is None:
            raise PersonalTriageConflictError("Excluded opportunity has no active exclusion decision.")
        target = validate_restore_target(target_status or exclusion["previous_status"])
        return self.repository.decide(opportunity_id, target, "restore", reason, exclusion["id"])
