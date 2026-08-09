from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from vocation.application.ports import DuplicateCaseRepository
from vocation.domain.research_bundle import DuplicateCase, canonical_subject_pair


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
