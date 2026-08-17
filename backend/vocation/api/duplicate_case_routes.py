from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request

from vocation.api.duplicate_case_schemas import DuplicateCaseReviewResponse, DuplicateDecisionPayload
from vocation.application.duplicate_cases import (
    DuplicateCaseNotFoundError,
    DuplicateCaseService,
    DuplicateDecisionConflictError,
)

router = APIRouter(prefix="/api/duplicate-cases", tags=["duplicate-cases"])


def _service(request: Request) -> DuplicateCaseService:
    return request.app.state.duplicate_case_service


@router.get("", response_model=list[DuplicateCaseReviewResponse])
def list_duplicate_cases(
    request: Request,
    subject_type: Literal["opportunity", "posting"] | None = Query(default=None),
    subject_id: str | None = Query(default=None),
) -> list[DuplicateCaseReviewResponse]:
    return [
        DuplicateCaseReviewResponse.model_validate(review)
        for review in _service(request).reviews(subject_type=subject_type, subject_id=subject_id)
    ]


@router.get("/{case_id}", response_model=DuplicateCaseReviewResponse)
def get_duplicate_case(case_id: str, request: Request) -> DuplicateCaseReviewResponse:
    review = _service(request).review(case_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Duplicate Case not found.")
    return DuplicateCaseReviewResponse.model_validate(review)


@router.post("/{case_id}/decisions", response_model=DuplicateCaseReviewResponse)
def decide_duplicate_case(
    case_id: str,
    payload: DuplicateDecisionPayload,
    request: Request,
) -> DuplicateCaseReviewResponse:
    service = _service(request)
    try:
        service.decide(case_id, outcome=payload.outcome, reason=payload.reason)
    except DuplicateCaseNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except DuplicateDecisionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    review = service.review(case_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Duplicate Case not found.")
    return DuplicateCaseReviewResponse.model_validate(review)
