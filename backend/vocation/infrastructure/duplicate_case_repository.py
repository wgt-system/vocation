from __future__ import annotations

from collections.abc import Callable
from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from vocation.application.duplicate_case_views import DuplicateSourceReferenceSummary, DuplicateSubjectSummary
from vocation.domain.research_bundle import DuplicateCase, DuplicateDecision, canonical_subject_pair
from vocation.infrastructure.duplicate_case_decision_model import DuplicateCaseDecisionModel
from vocation.infrastructure.models import (
    CompanyModel,
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

    def append_decision(self, decision: DuplicateDecision) -> DuplicateCase:
        with self.session_factory.begin() as session:
            case_model = session.get(DuplicateCaseModel, decision.duplicate_case_id)
            if case_model is None:
                raise DuplicateCaseValidationError("Duplicate Case does not exist.")
            latest_sequence = session.scalar(
                select(func.max(DuplicateCaseDecisionModel.sequence)).where(
                    DuplicateCaseDecisionModel.duplicate_case_id == decision.duplicate_case_id
                )
            )
            expected_sequence = (latest_sequence or 0) + 1
            if decision.sequence != expected_sequence:
                raise DuplicateCaseValidationError("Duplicate Decision sequence is stale.")
            session.add(
                DuplicateCaseDecisionModel(
                    id=decision.id,
                    duplicate_case_id=decision.duplicate_case_id,
                    sequence=decision.sequence,
                    outcome=decision.outcome,
                    reason=decision.reason,
                    decided_at=decision.decided_at,
                )
            )
            session.flush()
            return self._required_domain(case_model, session)

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

    def subject_summary(self, subject_type: str, subject_id: str) -> DuplicateSubjectSummary:
        with self.session_factory() as session:
            if subject_type == "opportunity":
                opportunity = session.get(OpportunityModel, subject_id)
                if opportunity is None:
                    raise DuplicateCaseValidationError("Duplicate Case Opportunity subject does not exist.")
                company = session.get(CompanyModel, opportunity.company_id)
                if company is None:
                    raise DuplicateCaseValidationError("Duplicate Case Opportunity company does not exist.")
                return DuplicateSubjectSummary(
                    subject_type="opportunity",
                    subject_id=opportunity.id,
                    title=opportunity.canonical_title,
                    context=company.canonical_name,
                )
            if subject_type == "posting":
                posting = session.get(PostingModel, subject_id)
                if posting is None:
                    raise DuplicateCaseValidationError("Duplicate Case Posting subject does not exist.")
                reference = session.get(SourceReferenceModel, posting.source_reference_id)
                if reference is None:
                    raise DuplicateCaseValidationError("Duplicate Case Posting source reference does not exist.")
                return DuplicateSubjectSummary(
                    subject_type="posting",
                    subject_id=posting.id,
                    title=posting.title,
                    context=reference.source.name,
                )
            raise DuplicateCaseValidationError("Duplicate Case subject type must be opportunity or posting.")

    def source_reference_summaries(self, source_reference_ids: tuple[str, ...]) -> tuple[DuplicateSourceReferenceSummary, ...]:
        with self.session_factory() as session:
            summaries: list[DuplicateSourceReferenceSummary] = []
            for reference_id in source_reference_ids:
                reference = session.get(SourceReferenceModel, reference_id)
                if reference is None:
                    raise DuplicateCaseValidationError("Duplicate Case Source Reference does not exist.")
                summaries.append(
                    DuplicateSourceReferenceSummary(
                        source_reference_id=reference.id,
                        source_name=reference.source.name,
                        display_label=reference.display_label,
                        url=reference.url,
                        observed_at=(reference.observed_at if reference.observed_at.tzinfo else reference.observed_at.replace(tzinfo=UTC)),
                    )
                )
            return tuple(summaries)

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
        decision_models = session.scalars(
            select(DuplicateCaseDecisionModel)
            .where(DuplicateCaseDecisionModel.duplicate_case_id == model.id)
            .order_by(DuplicateCaseDecisionModel.sequence)
        ).all()
        decisions = tuple(
            DuplicateDecision(
                id=decision.id,
                duplicate_case_id=decision.duplicate_case_id,
                sequence=decision.sequence,
                outcome=decision.outcome,
                reason=decision.reason,
                decided_at=decision.decided_at if decision.decided_at.tzinfo else decision.decided_at.replace(tzinfo=UTC),
            )
            for decision in decision_models
        )
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
            decisions=decisions,
        )
