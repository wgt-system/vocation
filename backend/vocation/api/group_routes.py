from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from vocation.api.schemas import (
    GroupMembershipResponse,
    OpportunityGroupMembershipPayload,
    OpportunityGroupPayload,
    OpportunityGroupReorderPayload,
    OpportunityGroupResponse,
)
from vocation.application.groups import OpportunityGroupService
from vocation.infrastructure.group_repository import (
    OpportunityGroupMembershipError,
    OpportunityGroupNotFoundError,
    OpportunityGroupValidationError,
    OpportunityNotFoundError,
)

router = APIRouter(prefix="/api/groups", tags=["groups"])


def _service(request: Request) -> OpportunityGroupService:
    return request.app.state.opportunity_group_service


def _response(group) -> OpportunityGroupResponse:
    return OpportunityGroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        group_type=group.group_type,
        memberships=[
            GroupMembershipResponse(
                opportunity_id=item.opportunity_id,
                position=item.position,
                opportunity_title=item.opportunity_title,
                company_name=item.company_name,
            )
            for item in group.memberships
        ],
    )


def _error(error: Exception) -> HTTPException:
    if isinstance(error, (OpportunityGroupNotFoundError, OpportunityNotFoundError)):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, OpportunityGroupMembershipError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, OpportunityGroupValidationError):
        return HTTPException(status_code=422, detail=str(error))
    raise error


@router.get("", response_model=list[OpportunityGroupResponse])
def list_groups(request: Request) -> list[OpportunityGroupResponse]:
    return [_response(group) for group in _service(request).list()]


@router.post("", response_model=OpportunityGroupResponse, status_code=201)
def create_group(payload: OpportunityGroupPayload, request: Request) -> OpportunityGroupResponse:
    try:
        return _response(_service(request).create(payload.name, payload.description, payload.group_type))
    except (OpportunityGroupValidationError, OpportunityGroupNotFoundError, OpportunityNotFoundError) as error:
        raise _error(error) from error


@router.get("/{group_id}", response_model=OpportunityGroupResponse)
def get_group(group_id: str, request: Request) -> OpportunityGroupResponse:
    group = _service(request).get(group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Opportunity Group not found.")
    return _response(group)


@router.put("/{group_id}", response_model=OpportunityGroupResponse)
def edit_group(group_id: str, payload: OpportunityGroupPayload, request: Request) -> OpportunityGroupResponse:
    try:
        return _response(
            _service(request).edit(group_id, name=payload.name, description=payload.description, group_type=payload.group_type)
        )
    except (OpportunityGroupValidationError, OpportunityGroupNotFoundError) as error:
        raise _error(error) from error


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: str, request: Request) -> Response:
    try:
        _service(request).delete(group_id)
    except OpportunityGroupNotFoundError as error:
        raise _error(error) from error
    return Response(status_code=204)


@router.post("/{group_id}/memberships", response_model=OpportunityGroupResponse)
def add_membership(group_id: str, payload: OpportunityGroupMembershipPayload, request: Request) -> OpportunityGroupResponse:
    try:
        return _response(_service(request).add_opportunity(group_id, payload.opportunity_id))
    except (OpportunityGroupMembershipError, OpportunityGroupNotFoundError, OpportunityNotFoundError) as error:
        raise _error(error) from error


@router.delete("/{group_id}/memberships/{opportunity_id}", response_model=OpportunityGroupResponse)
def remove_membership(group_id: str, opportunity_id: str, request: Request) -> OpportunityGroupResponse:
    try:
        return _response(_service(request).remove_opportunity(group_id, opportunity_id))
    except (OpportunityGroupMembershipError, OpportunityGroupNotFoundError, OpportunityNotFoundError) as error:
        raise _error(error) from error


@router.put("/{group_id}/order", response_model=OpportunityGroupResponse)
def reorder_group(group_id: str, payload: OpportunityGroupReorderPayload, request: Request) -> OpportunityGroupResponse:
    try:
        return _response(_service(request).reorder(group_id, payload.opportunity_ids))
    except (OpportunityGroupMembershipError, OpportunityGroupNotFoundError, OpportunityNotFoundError) as error:
        raise _error(error) from error
