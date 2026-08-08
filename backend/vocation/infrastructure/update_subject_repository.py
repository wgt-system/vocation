from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from vocation.domain.update_import import ExistingSubject, SubjectType
from vocation.infrastructure.models import CompanyModel, OpportunityModel, PostingModel


class SqlAlchemyUpdateSubjectRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, subject_type: SubjectType, subject_id: str) -> ExistingSubject | None:
        with self.session_factory() as session:
            if subject_type == "company":
                company = session.get(CompanyModel, subject_id)
                return ExistingSubject("company", company.id) if company else None
            if subject_type == "opportunity":
                opportunity = session.get(OpportunityModel, subject_id)
                if opportunity is None:
                    return None
                return ExistingSubject("opportunity", opportunity.id, company_id=opportunity.company_id)
            posting = session.get(PostingModel, subject_id)
            if posting is None:
                return None
            return ExistingSubject(
                "posting",
                posting.id,
                company_id=posting.company_id,
                opportunity_id=posting.opportunity_id,
            )
