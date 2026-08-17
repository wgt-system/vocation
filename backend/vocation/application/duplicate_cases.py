from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from vocation.application.duplicate_case_views import DuplicateCaseReview
from vocation.application.ports import DuplicateCaseRepository
from vocation.domain.research_bundle import (
    DUPLICATE_DECISION_OUTCOMES,
    DuplicateCase,
    DuplicateDecision,
    canonical_subject_pair,
)


class DuplicateCaseNotFoundError(LookupError):
    pass


class DuplicateDecisionConflictError(ValueError):
    pass


class DuplicateCaseService:
    def __init__(self, repository: DuplicateCaseRepository):
        self.repository = repository

    def create(
        self,
        *,
        research_import_id: str,
        subject_type: str,
        left_subject_id: str,
        right_subject_id: str,
        evidence_summary: str,
        confidence: float | None,
        source_reference_ids: list[str] | tuple[str, ...],
    ) -> DuplicateCase:
        left, right = canonical_subject_pair(subject_type, left_subject_id, right_subject_id)
        if not evidence_summary.strip():
            raise ValueError("Duplicate Case evidence summary must be nonblank.")
        if confidence is not None and not 0 <= confidence <= 1:
            raise ValueError("Duplicate Case confidence must be between 0 and 1.")
        if not source_reference_ids:
            raise ValueError("Duplicate Case requires at least one Source Reference.")
        existing = self.repository.find_by_pair(subject_type, left, right)
        if existing:
            return existing
        return self.repository.create(
            DuplicateCase(
                id=str(uuid4()),
                research_import_id=research_import_id,
                subject_type=subject_type,
                left_subject_id=left,
                right_subject_id=right,
                evidence_summary=evidence_summary.strip(),
                confidence=confidence,
                source_reference_ids=tuple(source_reference_ids),
                created_at=datetime.now(UTC),
            )
        )

    def get(self, case_id: str) -> DuplicateCase | None:
        return self.repository.get(case_id)

    def list(self, *, subject_type: str | None = None, subject_id: str | None = None) -> list[DuplicateCase]:
        return self.repository.list(subject_type=subject_type, subject_id=subject_id)

    def review(self, case_id: str) -> DuplicateCaseReview | None:
        case = self.repository.get(case_id)
        return self._review(case) if case is not None else None

    def reviews(self, *, subject_type: str | None = None, subject_id: str | None = None) -> list[DuplicateCaseReview]:
        return [self._review(case) for case in self.repository.list(subject_type=subject_type, subject_id=subject_id)]

    def decide(self, case_id: str, *, outcome: str, reason: str) -> DuplicateCase:
        case = self.repository.get(case_id)
        if case is None:
            raise DuplicateCaseNotFoundError("Duplicate Case not found.")
        if outcome not in DUPLICATE_DECISION_OUTCOMES:
            raise ValueError("Duplicate Decision outcome is invalid.")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("Duplicate Decision reason must be nonblank.")
        current = case.current_decision
        if current is not None and current.outcome == outcome:
            raise DuplicateDecisionConflictError("Duplicate Case already has this current decision outcome.")
        decision = DuplicateDecision(
            id=str(uuid4()),
            duplicate_case_id=case.id,
            sequence=len(case.decisions) + 1,
            outcome=outcome,
            reason=normalized_reason,
            decided_at=datetime.now(UTC),
        )
        return self.repository.append_decision(decision)

    def _review(self, case: DuplicateCase) -> DuplicateCaseReview:
        return DuplicateCaseReview(
            id=case.id,
            subject_type=case.subject_type,
            left_subject=self.repository.subject_summary(case.subject_type, case.left_subject_id),
            right_subject=self.repository.subject_summary(case.subject_type, case.right_subject_id),
            evidence_summary=case.evidence_summary,
            confidence=case.confidence,
            source_references=self.repository.source_reference_summaries(case.source_reference_ids),
            created_at=case.created_at,
            current_decision=case.current_decision,
            decision_history=case.decisions,
            is_reviewed=case.is_reviewed,
            is_resolved=case.is_resolved,
        )
