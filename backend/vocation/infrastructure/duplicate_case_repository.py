from __future__ import annotations

from collections.abc import Callable
from datetime import UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.research_bundle import DuplicateCase, canonical_subject_pair
from vocation.infrastructure.models import (
    DuplicateCaseModel,
    DuplicateCaseSourceReferenceModel,
    OpportunityModel,
    PostingModel,
    ResearchImportModel,
    SourceReferenceModel,
)


class DuplicateCaseValidationError(ValueError):
    pass


class SqlAlchemyDuplicateCaseRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, case_id: str) -> DuplicateCase | None:
        with self.session_factory() as session:
            return self._domain(session.get(DuplicateCaseModel, case_id), session)

    def find_by_pair(self, subject_type: str, left_subject_id: str, right_subject_id: str) -> DuplicateCase | None:
        left, right = canonical_subject_pair(subject_type, left_subject_id, right_subject_id)
        with self.session_factory() as session:
            model = session.scalar(
                select(DuplicateCaseModel).where(
                    DuplicateCaseModel.subject_type == subject_type,
                    DuplicateCaseModel.left_subject_id == left,
                    DuplicateCaseModel.right_subject_id == right,
                )
            )
            return self._domain(model, session)

    def create(self, case: DuplicateCase) -> DuplicateCase:
        left, right = canonical_subject_pair(case.subject_type, case.left_subject_id, case.right_subject_id)
        with self.session_factory.begin() as session:
            existing = session.scalar(
                select(DuplicateCaseModel).where(
                    DuplicateCaseModel.subject_type == case.subject_type,
                    DuplicateCaseModel.left_subject_id == left,
                    DuplicateCaseModel.right_subject_id == right,
                )
            )
            if existing:
                return self._required_domain(existing, session)
            self._validate_references(session, case)
            model = DuplicateCaseModel(
                id=case.id,
                research_import_id=case.research_import_id,
                subject_type=case.subject_type,
                left_subject_id=left,
                right_subject_id=right,
                evidence_summary=case.evidence_summary,
                confidence=case.confidence,
                created_at=case.created_at,
            )
            session.add(model)
            session.flush()
            for reference_id in case.source_reference_ids:
                session.add(
                    DuplicateCaseSourceReferenceModel(
                        duplicate_case_id=model.id,
                        source_reference_id=reference_id,
                    )
                )
            return self._required_domain(model, session)

    def list(self, *, subject_type: str | None = None, subject_id: str | None = None) -> list[DuplicateCase]:
        with self.session_factory() as session:
            statement = select(DuplicateCaseModel).order_by(DuplicateCaseModel.created_at, DuplicateCaseModel.id)
            if subject_type is not None:
                statement = statement.where(DuplicateCaseModel.subject_type == subject_type)
            if subject_id is not None:
                statement = statement.where(
                    (DuplicateCaseModel.left_subject_id == subject_id) | (DuplicateCaseModel.right_subject_id == subject_id)
                )
            return [self._required_domain(model, session) for model in session.scalars(statement).all()]

    @classmethod
    def _required_domain(cls, model: DuplicateCaseModel, session: Session) -> DuplicateCase:
        result = cls._domain(model, session)
        assert result is not None
        return result

    @staticmethod
    def _validate_references(session: Session, case: DuplicateCase) -> None:
        if session.get(ResearchImportModel, case.research_import_id) is None:
            raise DuplicateCaseValidationError("Research Import does not exist.")
        model = OpportunityModel if case.subject_type == "opportunity" else PostingModel
        if session.get(model, case.left_subject_id) is None or session.get(model, case.right_subject_id) is None:
            raise DuplicateCaseValidationError("Both Duplicate Case subjects must exist.")
        if not case.source_reference_ids:
            raise DuplicateCaseValidationError("Duplicate Case requires at least one Source Reference.")
        if len(set(case.source_reference_ids)) != len(case.source_reference_ids):
            raise DuplicateCaseValidationError("Duplicate Case Source References must be unique.")
        for reference_id in case.source_reference_ids:
            if session.get(SourceReferenceModel, reference_id) is None:
                raise DuplicateCaseValidationError("Every Duplicate Case Source Reference must exist.")

    @staticmethod
    def _domain(model: DuplicateCaseModel | None, session: Session) -> DuplicateCase | None:
        if model is None:
            return None
        links = session.scalars(
            select(DuplicateCaseSourceReferenceModel.source_reference_id)
            .where(DuplicateCaseSourceReferenceModel.duplicate_case_id == model.id)
            .order_by(DuplicateCaseSourceReferenceModel.source_reference_id)
        ).all()
        return DuplicateCase(
            id=model.id,
            research_import_id=model.research_import_id,
            subject_type=model.subject_type,
            left_subject_id=model.left_subject_id,
            right_subject_id=model.right_subject_id,
            evidence_summary=model.evidence_summary,
            confidence=model.confidence,
            source_reference_ids=tuple(links),
            created_at=model.created_at if model.created_at.tzinfo else model.created_at.replace(tzinfo=UTC),
        )
