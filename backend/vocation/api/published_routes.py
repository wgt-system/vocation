from __future__ import annotations

from fastapi import APIRouter, Request

from vocation.api.schemas import PublishedOpportunityOverviewResponse

router = APIRouter()


@router.get(
    "/published/v1/opportunity-overview",
    response_model=PublishedOpportunityOverviewResponse,
    include_in_schema=False,
)
def opportunity_overview(request: Request) -> PublishedOpportunityOverviewResponse:
    artifact = request.app.state.publication_service.generate()
    return PublishedOpportunityOverviewResponse.model_validate(artifact.as_dict())
