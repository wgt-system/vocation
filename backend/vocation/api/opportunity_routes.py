from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    DecisionResponse,
    ExclusionPayload,
    OpportunityDetailResponse,
    OpportunityListItemResponse,
    PersonalAssessmentPayload,
    PersonalAssessmentResponse,
    PersonalAssessmentRevisionPayload,
    RestorePayload,
    StatusPayload,
)
from vocation.application.opportunities import OpportunityQueryService
from vocation.application.personal_triage import PersonalTriageService

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


def _service(request: Request) -> PersonalTriageService:
    return request.app.state.personal_triage_service


def _error(error: Exception) -> HTTPException:
    if isinstance(error, LookupError):
        return HTTPException(status_code=404, detail="Opportunity or assessment not found.")
    return HTTPException(status_code=422, detail=str(error))


@router.get("/{opportunity_id}/assessments/personal", response_model=list[PersonalAssessmentResponse])
def personal_assessments(opportunity_id: str, request: Request) -> list[PersonalAssessmentResponse]:
    try:
        return [
            PersonalAssessmentResponse.model_validate(item) for item in _service(request).repository.current_assessments(opportunity_id)
        ]
    except Exception as error:
        raise _error(error) from error


@router.get("/{opportunity_id}/assessments/personal/history", response_model=list[PersonalAssessmentResponse])
def personal_assessment_history(opportunity_id: str, request: Request) -> list[PersonalAssessmentResponse]:
    try:
        return [PersonalAssessmentResponse.model_validate(item) for item in _service(request).repository.assessment_history(opportunity_id)]
    except Exception as error:
        raise _error(error) from error


@router.post("/{opportunity_id}/assessments/personal", response_model=PersonalAssessmentResponse, status_code=201)
def create_personal_assessment(opportunity_id: str, payload: PersonalAssessmentPayload, request: Request) -> PersonalAssessmentResponse:
    try:
        return PersonalAssessmentResponse.model_validate(
            _service(request).create_assessment(opportunity_id, payload.criterion_id, payload.value, payload.reasoning)
        )
    except Exception as error:
        raise _error(error) from error


@router.post("/{opportunity_id}/assessments/personal/{assessment_id}/revisions", response_model=PersonalAssessmentResponse, status_code=201)
def revise_personal_assessment(
    opportunity_id: str, assessment_id: str, payload: PersonalAssessmentRevisionPayload, request: Request
) -> PersonalAssessmentResponse:
    try:
        return PersonalAssessmentResponse.model_validate(
            _service(request).revise_assessment(opportunity_id, assessment_id, payload.value, payload.reasoning)
        )
    except Exception as error:
        raise _error(error) from error


@router.get("/{opportunity_id}/decisions", response_model=list[DecisionResponse])
def decision_history(opportunity_id: str, request: Request) -> list[DecisionResponse]:
    try:
        _service(request).repository.status(opportunity_id)
        return [DecisionResponse.model_validate(item) for item in _service(request).repository.decisions(opportunity_id)]
    except Exception as error:
        raise _error(error) from error


@router.post("/{opportunity_id}/status", response_model=DecisionResponse)
def change_status(opportunity_id: str, payload: StatusPayload, request: Request) -> DecisionResponse:
    try:
        return DecisionResponse.model_validate(_service(request).change_status(opportunity_id, payload.status, payload.reason))
    except Exception as error:
        raise _error(error) from error


@router.post("/{opportunity_id}/exclude", response_model=DecisionResponse)
def exclude(opportunity_id: str, payload: ExclusionPayload, request: Request) -> DecisionResponse:
    try:
        return DecisionResponse.model_validate(_service(request).exclude(opportunity_id, payload.reason))
    except Exception as error:
        raise _error(error) from error


@router.post("/{opportunity_id}/restore", response_model=DecisionResponse)
def restore(opportunity_id: str, payload: RestorePayload, request: Request) -> DecisionResponse:
    try:
        return DecisionResponse.model_validate(_service(request).restore(opportunity_id, payload.target_status, payload.reason))
    except Exception as error:
        raise _error(error) from error
