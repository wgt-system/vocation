from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    ActivationPayload,
    CriterionPayload,
    CriterionResponse,
    ReorderPayload,
)
from vocation.application.criteria import CriteriaService, CriterionNotFoundError
from vocation.domain.criteria import AssessmentCriterion, CriterionValidationError

router = APIRouter(prefix="/api/criteria", tags=["assessment criteria"])


def _service(request: Request) -> CriteriaService:
    return request.app.state.criteria_service


def _response(criterion: AssessmentCriterion) -> CriterionResponse:
    return CriterionResponse(**criterion.as_snapshot(), active=criterion.active, display_order=criterion.display_order)


def _domain(payload: CriterionPayload, *, revision: int = 1) -> AssessmentCriterion:
    return AssessmentCriterion(
        criterion_id=payload.criterion_id,
        display_name=payload.display_name,
        description=payload.description,
        value_type=payload.value_type,
        numeric_min=payload.numeric_min,
        numeric_max=payload.numeric_max,
        allowed_values=tuple(payload.allowed_values),
        applicable_subject_type=payload.applicable_subject_type,
        active=payload.active,
        display_order=payload.display_order,
        revision=revision,
    )


@router.get("", response_model=list[CriterionResponse])
def list_criteria(request: Request) -> list[CriterionResponse]:
    return [_response(item) for item in _service(request).list()]


@router.post("", response_model=CriterionResponse, status_code=201)
def create_criterion(payload: CriterionPayload, request: Request) -> CriterionResponse:
    try:
        return _response(_service(request).create(_domain(payload)))
    except (ValueError, CriterionValidationError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.put("/{criterion_id}", response_model=CriterionResponse)
def edit_criterion(criterion_id: str, payload: CriterionPayload, request: Request) -> CriterionResponse:
    try:
        return _response(_service(request).update(criterion_id, _domain(payload)))
    except CriterionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Criterion not found.") from error
    except CriterionValidationError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/{criterion_id}/activation", response_model=CriterionResponse)
def activate_criterion(criterion_id: str, payload: ActivationPayload, request: Request) -> CriterionResponse:
    try:
        return _response(_service(request).set_active(criterion_id, payload.active))
    except CriterionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Criterion not found.") from error


@router.post("/reorder", response_model=list[CriterionResponse])
def reorder_criteria(payload: ReorderPayload, request: Request) -> list[CriterionResponse]:
    try:
        return [_response(item) for item in _service(request).reorder(payload.criterion_ids)]
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
