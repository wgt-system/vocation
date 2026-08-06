from __future__ import annotations

from dataclasses import replace

from vocation.application.ports import CriteriaRepository
from vocation.domain.criteria import (
    AssessmentCriterion,
    IncompatibleCriterionChangeError,
    validate_criterion,
)


class CriterionNotFoundError(LookupError):
    pass


class CriteriaService:
    def __init__(self, repository: CriteriaRepository):
        self.repository = repository

    def list(self, *, active_only: bool = False) -> list[AssessmentCriterion]:
        return self.repository.list(active_only=active_only)

    def create(self, criterion: AssessmentCriterion) -> AssessmentCriterion:
        validate_criterion(criterion)
        if self.repository.get(criterion.criterion_id):
            raise ValueError(f"Criterion '{criterion.criterion_id}' already exists.")
        return self.repository.create(criterion)

    def update(self, criterion_id: str, replacement: AssessmentCriterion) -> AssessmentCriterion:
        existing = self.repository.get(criterion_id)
        if existing is None:
            raise CriterionNotFoundError(criterion_id)
        if replacement.criterion_id != criterion_id:
            raise IncompatibleCriterionChangeError("Criterion ID cannot be changed.")
        validate_criterion(replacement)
        if self.repository.is_referenced(criterion_id) and existing.semantic_signature() != replacement.semantic_signature():
            raise IncompatibleCriterionChangeError(
                "A referenced criterion cannot change value type, scale, allowed values, or subject type; create a new ID."
            )
        changed = replace(replacement, revision=existing.revision + 1)
        return self.repository.update(changed)

    def set_active(self, criterion_id: str, active: bool) -> AssessmentCriterion:
        if self.repository.get(criterion_id) is None:
            raise CriterionNotFoundError(criterion_id)
        return self.repository.set_active(criterion_id, active)

    def reorder(self, criterion_ids: list[str]) -> list[AssessmentCriterion]:
        known_ids = {item.criterion_id for item in self.repository.list()}
        if len(criterion_ids) != len(set(criterion_ids)) or set(criterion_ids) != known_ids:
            raise ValueError("Reorder must contain every criterion ID exactly once.")
        return self.repository.reorder(criterion_ids)
