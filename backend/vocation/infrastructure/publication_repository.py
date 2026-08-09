from __future__ import annotations

from sqlalchemy import select

from vocation.application.publication import (
    OpportunityOverviewPublicationRepository,
    PublicationOpportunitySource,
    PublicationWorkLocation,
)
from vocation.infrastructure.models import CompanyModel, OpportunityModel, PostingModel, WorkLocationModel


class SqlAlchemyOpportunityOverviewPublicationRepository(OpportunityOverviewPublicationRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def load_opportunities(self) -> tuple[PublicationOpportunitySource, ...]:
        with self._session_factory() as session:
            companies = {company.id: company for company in session.scalars(select(CompanyModel)).all()}
            locations_by_opportunity: dict[str, list[WorkLocationModel]] = {}
            for location in session.scalars(select(WorkLocationModel)).all():
                locations_by_opportunity.setdefault(location.opportunity_id, []).append(location)
            postings_by_opportunity: dict[str, int] = {}
            for posting in session.scalars(select(PostingModel)).all():
                postings_by_opportunity[posting.opportunity_id] = postings_by_opportunity.get(posting.opportunity_id, 0) + 1

            result: list[PublicationOpportunitySource] = []
            for opportunity in session.scalars(select(OpportunityModel)).all():
                company = companies[opportunity.company_id]
                result.append(
                    PublicationOpportunitySource(
                        opportunity_ref=opportunity.id,
                        title=opportunity.canonical_title,
                        company_ref=company.id,
                        company_name=company.canonical_name,
                        work_locations=tuple(
                            PublicationWorkLocation(
                                label=location.label,
                                city=location.city,
                                region=location.region,
                                country_code=location.country_code,
                                precision=location.precision,
                            )
                            for location in locations_by_opportunity.get(opportunity.id, [])
                        ),
                        posting_count=postings_by_opportunity.get(opportunity.id, 0),
                    )
                )
            return tuple(result)
