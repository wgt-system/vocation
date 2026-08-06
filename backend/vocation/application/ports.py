from __future__ import annotations

from typing import Protocol

from vocation.domain.criteria import AssessmentCriterion


class CriteriaRepository(Protocol):
    def list(self, *, active_only: bool = False) -> list[AssessmentCriterion]: ...
    def get(self, criterion_id: str) -> AssessmentCriterion | None: ...
    def create(self, criterion: AssessmentCriterion) -> AssessmentCriterion: ...
    def update(self, criterion: AssessmentCriterion) -> AssessmentCriterion: ...
    def set_active(self, criterion_id: str, active: bool) -> AssessmentCriterion: ...
    def reorder(self, criterion_ids: list[str]) -> list[AssessmentCriterion]: ...
    def is_referenced(self, criterion_id: str) -> bool: ...


class PromptRunRepository(Protocol):
    def save_initial(
        self,
        *,
        search_profile: str,
        constraints: list[str],
        as_of_date: str,
        criteria_snapshot: list[dict],
        prompt_text: str,
    ) -> str: ...
