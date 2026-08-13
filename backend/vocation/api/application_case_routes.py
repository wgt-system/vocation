from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from vocation.api.schemas import (
    ApplicationCaseLifecyclePayload,
    ApplicationCaseResponse,
    ApplicationLifecycleEventResponse,
    ApplicationMaterialPayload,
    ApplicationMaterialResponse,
    ApplicationMaterialRevisionPayload,
)
from vocation.application.application_cases import (
    ApplicationCaseNotFoundError,
    ApplicationCaseService,
    ApplicationMaterialNotFoundError,
    OpportunityNotFoundError,
)
from vocation.domain.application_cases import ApplicationCaseConflictError, ApplicationCaseError

router = APIRouter(tags=["application-cases"])


def _service(request: Request) -> ApplicationCaseService:
    return request.app.state.application_case_service


def _case_response(case) -> ApplicationCaseResponse:
    return ApplicationCaseResponse(
        id=case.id,
        opportunity_id=case.opportunity_id,
        lifecycle=case.lifecycle,
        created_at=case.created_at,
        updated_at=case.updated_at,
        lifecycle_events=[
            ApplicationLifecycleEventResponse(
                previous_status=event.previous_status,
                resulting_status=event.resulting_status,
                occurred_at=event.occurred_at,
            )
            for event in case.lifecycle_events
        ],
    )


def _material_response(material) -> ApplicationMaterialResponse:
    return ApplicationMaterialResponse(
        id=material.id,
        application_case_id=material.application_case_id,
        kind=material.kind,
        display_name=material.display_name,
        revision=material.revision,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )


def _raise_error(error: Exception) -> None:
    if isinstance(error, (ApplicationCaseNotFoundError, ApplicationMaterialNotFoundError, OpportunityNotFoundError)):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, ApplicationCaseConflictError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, ApplicationCaseError):
        raise HTTPException(status_code=422, detail=str(error)) from error
    raise error


@router.get("/api/opportunities/{opportunity_id}/application-cases", response_model=list[ApplicationCaseResponse])
def list_cases(opportunity_id: str, request: Request) -> list[ApplicationCaseResponse]:
    try:
        return [_case_response(case) for case in _service(request).list_for_opportunity(opportunity_id)]
    except (ApplicationCaseNotFoundError, OpportunityNotFoundError) as error:
        _raise_error(error)
    raise AssertionError("unreachable")


@router.post(
    "/api/opportunities/{opportunity_id}/application-cases",
    response_model=ApplicationCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case(opportunity_id: str, request: Request) -> ApplicationCaseResponse:
    try:
        return _case_response(_service(request).create_case(opportunity_id))
    except (ApplicationCaseNotFoundError, OpportunityNotFoundError, ApplicationCaseConflictError, ApplicationCaseError) as error:
        _raise_error(error)
    raise AssertionError("unreachable")


@router.get("/api/application-cases/{case_id}", response_model=ApplicationCaseResponse)
def get_case(case_id: str, request: Request) -> ApplicationCaseResponse:
    case = _service(request).get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Application Case '{case_id}' does not exist.")
    return _case_response(case)


@router.post("/api/application-cases/{case_id}/lifecycle", response_model=ApplicationCaseResponse)
def change_lifecycle(case_id: str, payload: ApplicationCaseLifecyclePayload, request: Request) -> ApplicationCaseResponse:
    try:
        return _case_response(_service(request).change_lifecycle(case_id, payload.lifecycle))
    except (ApplicationCaseNotFoundError, ApplicationCaseConflictError, ApplicationCaseError) as error:
        _raise_error(error)
    raise AssertionError("unreachable")


@router.get("/api/application-cases/{case_id}/materials", response_model=list[ApplicationMaterialResponse])
def list_materials(case_id: str, request: Request) -> list[ApplicationMaterialResponse]:
    try:
        return [_material_response(material) for material in _service(request).list_materials(case_id)]
    except ApplicationCaseNotFoundError as error:
        _raise_error(error)
    raise AssertionError("unreachable")


@router.post(
    "/api/application-cases/{case_id}/materials",
    response_model=ApplicationMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material(case_id: str, payload: ApplicationMaterialPayload, request: Request) -> ApplicationMaterialResponse:
    try:
        return _material_response(_service(request).create_material(case_id, payload.kind, payload.display_name))
    except (ApplicationCaseNotFoundError, ApplicationCaseError) as error:
        _raise_error(error)
    raise AssertionError("unreachable")


@router.post(
    "/api/application-materials/{material_id}/revisions",
    response_model=ApplicationMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def revise_material(material_id: str, payload: ApplicationMaterialRevisionPayload, request: Request) -> ApplicationMaterialResponse:
    try:
        return _material_response(_service(request).revise_material(material_id, payload.display_name))
    except (ApplicationMaterialNotFoundError, ApplicationCaseConflictError, ApplicationCaseError) as error:
        _raise_error(error)
    raise AssertionError("unreachable")
