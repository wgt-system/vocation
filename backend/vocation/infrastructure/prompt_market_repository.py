from __future__ import annotations

import json
from collections.abc import Callable
from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.prompt_market import (
    MarketAssessment,
    MarketCompany,
    MarketDuplicateCase,
    MarketLocation,
    MarketObservation,
    MarketOpportunity,
    MarketPosting,
    PromptMarket,
    SubjectType,
)
from vocation.infrastructure.models import (
    CompanyModel,
    DuplicateCaseModel,
    DuplicateCaseSourceReferenceModel,
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    SourceReferenceModel,
    WorkLocationModel,
)


class SqlAlchemyPromptMarketRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def load_market(self) -> PromptMarket:
        with self.session_factory() as session:
            references = {reference.id: reference.url for reference in session.scalars(select(SourceReferenceModel)).all()}
            companies = session.scalars(select(CompanyModel).order_by(CompanyModel.id)).all()
            opportunities = session.scalars(select(OpportunityModel).order_by(OpportunityModel.id)).all()
            postings = session.scalars(select(PostingModel).order_by(PostingModel.id)).all()
            locations = session.scalars(select(WorkLocationModel).order_by(WorkLocationModel.id)).all()
            observations = session.scalars(select(ObservationModel).order_by(ObservationModel.id)).all()
            assessments = session.scalars(select(ExternalAssessmentModel).order_by(ExternalAssessmentModel.id)).all()
            duplicate_cases = session.scalars(select(DuplicateCaseModel).order_by(DuplicateCaseModel.id)).all()
            duplicate_links = session.scalars(
                select(DuplicateCaseSourceReferenceModel).order_by(
                    DuplicateCaseSourceReferenceModel.duplicate_case_id,
                    DuplicateCaseSourceReferenceModel.source_reference_id,
                )
            ).all()

            locations_by_opportunity: dict[str, list[MarketLocation]] = {}
            for location in locations:
                locations_by_opportunity.setdefault(location.opportunity_id, []).append(
                    MarketLocation(
                        label=location.label,
                        city=location.city,
                        region=location.region,
                        country_code=location.country_code,
                        precision=location.precision,
                        source_url=references.get(location.source_reference_id),
                    )
                )
            links_by_case: dict[str, list[str]] = {}
            for link in duplicate_links:
                url = references.get(link.source_reference_id)
                if url is not None:
                    links_by_case.setdefault(link.duplicate_case_id, []).append(url)

            return PromptMarket(
                companies=tuple(
                    MarketCompany(company.id, company.canonical_name, references.get(company.source_reference_id)) for company in companies
                ),
                opportunities=tuple(
                    MarketOpportunity(
                        opportunity.id,
                        opportunity.company_id,
                        opportunity.canonical_title,
                        tuple(locations_by_opportunity.get(opportunity.id, [])),
                        references.get(opportunity.source_reference_id),
                    )
                    for opportunity in opportunities
                ),
                postings=tuple(
                    MarketPosting(
                        posting.id,
                        posting.company_id,
                        posting.opportunity_id,
                        posting.title,
                        posting.external_posting_id,
                        posting.canonical_url,
                        posting.published_at,
                        posting.observed_at,
                    )
                    for posting in postings
                ),
                observations=tuple(
                    MarketObservation(
                        cast(SubjectType, observation.subject_type),
                        observation.subject_id,
                        observation.observation_type,
                        json.loads(observation.value_json),
                        observation.observed_at,
                        observation.confidence,
                        observation.evidence_summary,
                        references.get(observation.source_reference_id),
                    )
                    for observation in observations
                ),
                assessments=tuple(
                    MarketAssessment(
                        cast(SubjectType, assessment.subject_type),
                        assessment.subject_id,
                        assessment.criterion_id,
                        json.loads(assessment.value_json),
                        assessment.created_at,
                        assessment.reasoning,
                        tuple(
                            references[reference_id]
                            for reference_id in json.loads(assessment.source_reference_ids_json)
                            if reference_id in references
                        ),
                    )
                    for assessment in assessments
                ),
                duplicate_cases=tuple(
                    MarketDuplicateCase(
                        case.id,
                        cast(
                            Literal["opportunity", "posting"],
                            case.subject_type,
                        ),
                        case.left_subject_id,
                        case.right_subject_id,
                        case.evidence_summary,
                        case.confidence,
                        tuple(links_by_case.get(case.id, [])),
                    )
                    for case in duplicate_cases
                ),
            )
