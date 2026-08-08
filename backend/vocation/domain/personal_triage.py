from __future__ import annotations

from typing import Any

from vocation.domain.criteria import AssessmentCriterion, validate_assessment_value

TRACKING_STATUSES = ("new", "to_review", "interesting", "shortlisted", "deferred", "excluded", "archived")
NON_EXCLUDED_STATUSES = tuple(status for status in TRACKING_STATUSES if status != "excluded")


class PersonalTriageError(ValueError):
    pass


class PersonalTriageConflictError(PersonalTriageError):
    pass


def validate_tracking_status(status: str) -> None:
    if status not in TRACKING_STATUSES:
        raise PersonalTriageError(f"Unsupported tracking status: {status}.")


def validate_personal_assessment(criterion: AssessmentCriterion, value: Any) -> None:
    if not criterion.active:
        raise PersonalTriageError("Only active assessment criteria can receive a new personal assessment.")
    if criterion.applicable_subject_type != "opportunity":
        raise PersonalTriageError("Personal opportunity assessments require an opportunity criterion.")
    if not validate_assessment_value(criterion, value):
        raise PersonalTriageError(f"Value is invalid for criterion '{criterion.criterion_id}'.")


def validate_exclusion_reason(reason: str) -> str:
    normalized = reason.strip()
    if not normalized:
        raise PersonalTriageError("Exclusion requires a non-empty reason.")
    return normalized


def validate_restore_target(status: str) -> str:
    target = status
    validate_tracking_status(target)
    if target == "excluded":
        raise PersonalTriageError("Restore target cannot be excluded.")
    return target
