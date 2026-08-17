from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DuplicateSubjectType = Literal["opportunity", "posting"]
DuplicateDecisionOutcome = Literal[
    "confirmed_duplicate",
    "confirmed_distinct",
    "related_but_distinct",
    "keep_unresolved",
]


class DuplicateDecisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: DuplicateDecisionOutcome
    reason: str = Field(min_length=1)


class DuplicateDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    duplicate_case_id: str
    sequence: int
    outcome: DuplicateDecisionOutcome
    reason: str
    decided_at: datetime


class DuplicateSubjectSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject_type: DuplicateSubjectType
    subject_id: str
    title: str
    context: str


class DuplicateSourceReferenceSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_reference_id: str
    source_name: str
    display_label: str | None
    url: str
    observed_at: datetime


class DuplicateCaseReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject_type: DuplicateSubjectType
    left_subject: DuplicateSubjectSummaryResponse
    right_subject: DuplicateSubjectSummaryResponse
    evidence_summary: str
    confidence: float | None
    source_references: list[DuplicateSourceReferenceSummaryResponse]
    created_at: datetime
    current_decision: DuplicateDecisionResponse | None
    decision_history: list[DuplicateDecisionResponse]
    is_reviewed: bool
    is_resolved: bool
