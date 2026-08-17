from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from vocation.application.fit import OpportunityFitNotFoundError, OpportunityFitService, SearchProfileRequiredError
from vocation.domain.fit import OpportunityFit

router = APIRouter(tags=["opportunity-fit"])


class CriterionContributionResponse(BaseModel):
    criterion_id: str
    criterion_name: str
    weight: float
    required: bool
    status: Literal["scored", "missing", "unscorable"]
    value: Any | None
    origin: str | None
    score: float | None
    weighted_points: float | None
    explanation: str


class OpportunityFitResponse(BaseModel):
    opportunity_id: str
    search_profile_id: str
    search_profile_revision: int
    candidate_profile_revision: int | None
    hard_constraint_status: Literal["pass", "fail", "unknown"]
    weighted_fit_score: float | None
    evidence_completeness: float
    contributions: list[CriterionContributionResponse]
    hard_failures: list[str]
    hard_unknowns: list[str]
    missing_evidence: list[str]


def _service(request: Request) -> OpportunityFitService:
    return request.app.state.opportunity_fit_service


def _response(fit: OpportunityFit) -> OpportunityFitResponse:
    return OpportunityFitResponse(
        opportunity_id=fit.opportunity_id,
        search_profile_id=fit.search_profile_id,
        search_profile_revision=fit.search_profile_revision,
        candidate_profile_revision=fit.candidate_profile_revision,
        hard_constraint_status=fit.hard_constraint_status,
        weighted_fit_score=fit.weighted_fit_score,
        evidence_completeness=fit.evidence_completeness,
        contributions=[CriterionContributionResponse(**item.__dict__) for item in fit.contributions],
        hard_failures=list(fit.hard_failures),
        hard_unknowns=list(fit.hard_unknowns),
        missing_evidence=list(fit.missing_evidence),
    )


def _error(error: Exception) -> HTTPException:
    if isinstance(error, OpportunityFitNotFoundError):
        return HTTPException(status_code=404, detail=f"Opportunity '{error}' does not exist.")
    if isinstance(error, SearchProfileRequiredError):
        return HTTPException(status_code=409, detail=str(error))
    raise error


@router.get("/api/opportunity-fit", response_model=list[OpportunityFitResponse])
def list_opportunity_fit(
    request: Request,
    search_profile_id: str | None = None,
    opportunity_id: list[str] | None = Query(default=None),
) -> list[OpportunityFitResponse]:
    try:
        return [_response(item) for item in _service(request).list(search_profile_id, opportunity_id)]
    except (OpportunityFitNotFoundError, SearchProfileRequiredError) as error:
        raise _error(error) from error


@router.get("/api/opportunities/{opportunity_id}/fit", response_model=OpportunityFitResponse)
def get_opportunity_fit(
    opportunity_id: str,
    request: Request,
    search_profile_id: str | None = None,
) -> OpportunityFitResponse:
    try:
        return _response(_service(request).get(opportunity_id, search_profile_id))
    except (OpportunityFitNotFoundError, SearchProfileRequiredError) as error:
        raise _error(error) from error
