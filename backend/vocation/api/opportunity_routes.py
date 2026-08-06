from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import OpportunityDetailResponse, OpportunityListItemResponse
from vocation.application.opportunities import OpportunityQueryService

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityListItemResponse])
def list_opportunities(request: Request) -> list[OpportunityListItemResponse]:
    service: OpportunityQueryService = request.app.state.opportunity_service
    return [OpportunityListItemResponse.model_validate(item) for item in service.list()]


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
def opportunity_detail(opportunity_id: str, request: Request) -> OpportunityDetailResponse:
    service: OpportunityQueryService = request.app.state.opportunity_service
    detail = service.detail(opportunity_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return OpportunityDetailResponse.model_validate(detail)
