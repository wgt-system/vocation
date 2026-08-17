from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from vocation.domain.research_bundle import DuplicateDecision


@dataclass(frozen=True)
class DuplicateSubjectSummary:
    subject_type: str
    subject_id: str
    title: str
    context: str


@dataclass(frozen=True)
class DuplicateSourceReferenceSummary:
    source_reference_id: str
    source_name: str
    display_label: str | None
    url: str
    observed_at: datetime


@dataclass(frozen=True)
class DuplicateCaseReview:
    id: str
    subject_type: str
    left_subject: DuplicateSubjectSummary
    right_subject: DuplicateSubjectSummary
    evidence_summary: str
    confidence: float | None
    source_references: tuple[DuplicateSourceReferenceSummary, ...]
    created_at: datetime
    current_decision: DuplicateDecision | None
    decision_history: tuple[DuplicateDecision, ...]
    is_reviewed: bool
    is_resolved: bool
