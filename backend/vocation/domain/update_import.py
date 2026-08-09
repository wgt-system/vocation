from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

SubjectType = Literal["company", "opportunity", "posting"]
PlanAction = Literal["create", "reuse"]


@dataclass(frozen=True)
class PromptContextSubject:
    correlation_ref: str
    subject_type: SubjectType
    subject_id: str
    is_target: bool


@dataclass(frozen=True)
class PromptContextSnapshot:
    prompt_context_ref: str
    scope_type: str
    as_of_date: date
    scope_json: dict
    subjects: tuple[PromptContextSubject, ...]
    created_at: datetime | None = None

    def subject_by_correlation(self, correlation_ref: str) -> PromptContextSubject | None:
        return next((subject for subject in self.subjects if subject.correlation_ref == correlation_ref), None)


@dataclass(frozen=True)
class ExistingSubject:
    subject_type: SubjectType
    subject_id: str
    company_id: str | None = None
    opportunity_id: str | None = None


@dataclass(frozen=True)
class PlannedSubject:
    bundle_local_id: str
    subject_type: SubjectType
    subject_id: str
    action: PlanAction
    is_target: bool


@dataclass(frozen=True)
class PlannedDuplicateCase:
    bundle_local_id: str
    subject_type: Literal["opportunity", "posting"]
    left_subject_id: str
    right_subject_id: str
    action: PlanAction
    evidence_summary: str
    confidence: float | None
    source_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class UpdateImportPlan:
    prompt_context_ref: str
    scope_type: str
    companies: tuple[PlannedSubject, ...]
    opportunities: tuple[PlannedSubject, ...]
    postings: tuple[PlannedSubject, ...]
    duplicate_cases: tuple[PlannedDuplicateCase, ...]

    def subjects(self, subject_type: SubjectType) -> tuple[PlannedSubject, ...]:
        return {
            "company": self.companies,
            "opportunity": self.opportunities,
            "posting": self.postings,
        }[subject_type]
