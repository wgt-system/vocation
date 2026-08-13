from __future__ import annotations

from fastapi import APIRouter, Request

from vocation.api.schemas import PublishedMapProjectionResponse, PublishedOpportunityOverviewResponse

router = APIRouter()


@router.get(
    "/published/v1/opportunity-overview",
    response_model=PublishedOpportunityOverviewResponse,
    include_in_schema=False,
)
def opportunity_overview(request: Request) -> PublishedOpportunityOverviewResponse:
    artifact = request.app.state.publication_service.generate()
    return PublishedOpportunityOverviewResponse.model_validate(artifact.as_dict())


@router.get(
    "/published/v1/map-projection",
    response_model=PublishedMapProjectionResponse,
    include_in_schema=False,
)
def map_projection(request: Request) -> PublishedMapProjectionResponse:
    artifact = request.app.state.map_publication_service.generate()
    return PublishedMapProjectionResponse.model_validate(artifact.as_dict())
