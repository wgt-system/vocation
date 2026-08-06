from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from vocation.application.opportunities import OpportunityQueryService


router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("")
def list_opportunities(request: Request) -> list[dict[str, Any]]:
    service: OpportunityQueryService = request.app.state.opportunity_service
    return service.list()


@router.get("/{opportunity_id}")
def opportunity_detail(opportunity_id: str, request: Request) -> dict[str, Any]:
    service: OpportunityQueryService = request.app.state.opportunity_service
    detail = service.detail(opportunity_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return detail
