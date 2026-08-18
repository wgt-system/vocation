from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from vocation.application.opportunity_notes import OpportunityNoteService

router = APIRouter(prefix="/api/opportunities", tags=["opportunity-notes"])


class OpportunityNotePayload(BaseModel):
    content: str = Field(max_length=50_000)


class OpportunityNoteResponse(BaseModel):
    opportunity_id: str
    content: str
    updated_at: str


def _service(request: Request) -> OpportunityNoteService:
    return request.app.state.opportunity_note_service


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Opportunity '{error}' does not exist.")


@router.get("/{opportunity_id}/note", response_model=OpportunityNoteResponse | None)
def get_opportunity_note(opportunity_id: str, request: Request) -> OpportunityNoteResponse | None:
    try:
        note = _service(request).get(opportunity_id)
        return OpportunityNoteResponse(**note) if note is not None else None
    except LookupError as error:
        raise _not_found(error) from error


@router.put("/{opportunity_id}/note", response_model=OpportunityNoteResponse | None)
def save_opportunity_note(
    opportunity_id: str,
    payload: OpportunityNotePayload,
    request: Request,
) -> OpportunityNoteResponse | None:
    try:
        note = _service(request).save(opportunity_id, payload.content)
        return OpportunityNoteResponse(**note) if note is not None else None
    except LookupError as error:
        raise _not_found(error) from error
