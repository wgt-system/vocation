from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALUE_TYPES = {"numeric", "boolean", "categorical", "text"}
SUBJECT_TYPES = {"company", "opportunity", "posting"}


class CriterionValidationError(ValueError):
    pass


class IncompatibleCriterionChangeError(CriterionValidationError):
    pass


@dataclass(frozen=True)
class AssessmentCriterion:
    criterion_id: str
    display_name: str
    description: str
    value_type: str
    applicable_subject_type: str
    active: bool
    display_order: int
    revision: int = 1
    numeric_min: float | None = None
    numeric_max: float | None = None
    allowed_values: tuple[str, ...] = ()

    def semantic_signature(self) -> tuple[Any, ...]:
        return (
            self.value_type,
            self.numeric_min,
            self.numeric_max,
            self.allowed_values,
            self.applicable_subject_type,
        )

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "display_name": self.display_name,
            "description": self.description,
            "value_type": self.value_type,
            "numeric_min": self.numeric_min,
            "numeric_max": self.numeric_max,
            "allowed_values": list(self.allowed_values),
            "applicable_subject_type": self.applicable_subject_type,
            "revision": self.revision,
        }


def validate_criterion(criterion: AssessmentCriterion) -> None:
    if not criterion.criterion_id or any(character.isspace() for character in criterion.criterion_id):
        raise CriterionValidationError("Criterion ID must be non-empty and contain no whitespace.")
    if not criterion.display_name.strip():
        raise CriterionValidationError("Display name is required.")
    if criterion.value_type not in VALUE_TYPES:
        raise CriterionValidationError(f"Unsupported value type: {criterion.value_type}")
    if criterion.applicable_subject_type not in SUBJECT_TYPES:
        raise CriterionValidationError("Applicable subject type must be company, opportunity, or posting.")
    if criterion.value_type == "numeric":
        if criterion.numeric_min is None or criterion.numeric_max is None:
            raise CriterionValidationError("Numeric criteria require minimum and maximum values.")
        if criterion.numeric_min >= criterion.numeric_max:
            raise CriterionValidationError("Numeric minimum must be smaller than maximum.")
        if criterion.allowed_values:
            raise CriterionValidationError("Numeric criteria cannot define categorical values.")
    elif criterion.numeric_min is not None or criterion.numeric_max is not None:
        raise CriterionValidationError("Only numeric criteria may define numeric bounds.")
    if criterion.value_type == "categorical" and not criterion.allowed_values:
        raise CriterionValidationError("Categorical criteria require allowed values.")
    if criterion.value_type != "categorical" and criterion.allowed_values:
        raise CriterionValidationError("Only categorical criteria may define allowed values.")
    if len(set(criterion.allowed_values)) != len(criterion.allowed_values):
        raise CriterionValidationError("Allowed values must be unique.")


def validate_assessment_value(criterion: AssessmentCriterion, value: Any) -> bool:
    if criterion.value_type == "numeric":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and criterion.numeric_min <= value <= criterion.numeric_max
        )
    if criterion.value_type == "boolean":
        return isinstance(value, bool)
    if criterion.value_type == "categorical":
        return isinstance(value, str) and value in criterion.allowed_values
    return isinstance(value, str)
