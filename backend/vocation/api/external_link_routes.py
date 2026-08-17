from __future__ import annotations

from datetime import UTC

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import ExternalLinkOpenPayload, ExternalLinkResponse
from vocation.application.external_navigation import (
    BrowserOpenError,
    ExternalLinkNotFoundError,
    ExternalNavigationService,
    OpportunityNotFoundError,
)

router = APIRouter(prefix="/api/external-links", tags=["external-links"])


def _service(request: Request) -> ExternalNavigationService:
    return request.app.state.external_navigation_service


def _response(link) -> ExternalLinkResponse:
    observed_at = link.observed_at
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=UTC)
    return ExternalLinkResponse(
        posting_id=link.posting_id,
        source_id=link.source_id,
        source_name=link.source_name,
        source_type=link.source_type,
        url=link.url,
        display_label=link.display_label,
        availability=link.availability,
        observed_at=observed_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        preferred=link.preferred,
    )


@router.get("/opportunities/{opportunity_id}", response_model=list[ExternalLinkResponse])
def opportunity_links(opportunity_id: str, request: Request) -> list[ExternalLinkResponse]:
    try:
        return [_response(link) for link in _service(request).links_for_opportunity(opportunity_id)]
    except OpportunityNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/opportunities/{opportunity_id}/open", response_model=ExternalLinkResponse)
def open_opportunity(opportunity_id: str, payload: ExternalLinkOpenPayload, request: Request) -> ExternalLinkResponse:
    try:
        return _response(_service(request).open_opportunity(opportunity_id, payload.posting_id))
    except OpportunityNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ExternalLinkNotFoundError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except BrowserOpenError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
