from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from vocation.api.profile_mapping import candidate_from_payload, candidate_response, search_from_payload, search_response
from vocation.api.profile_schemas import CandidateProfilePayload, CandidateProfileResponse, SearchProfilePayload, SearchProfileResponse
from vocation.application.profiles import ProfileService
from vocation.domain.profiles import ProfileValidationError
from vocation.infrastructure.profile_repository import SearchProfileConflictError, SearchProfileNotFoundError

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _service(request: Request) -> ProfileService:
    return request.app.state.profile_service


def _error(error: Exception) -> HTTPException:
    if isinstance(error, SearchProfileNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, SearchProfileConflictError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, ProfileValidationError):
        return HTTPException(status_code=422, detail=str(error))
    raise error


@router.get("/candidate", response_model=CandidateProfileResponse | None)
def get_candidate_profile(request: Request) -> CandidateProfileResponse | None:
    profile = _service(request).get_candidate_profile()
    return None if profile is None else candidate_response(profile)


@router.put("/candidate", response_model=CandidateProfileResponse)
def save_candidate_profile(payload: CandidateProfilePayload, request: Request) -> CandidateProfileResponse:
    try:
        return candidate_response(_service(request).save_candidate_profile(candidate_from_payload(payload)))
    except ProfileValidationError as error:
        raise _error(error) from error


@router.get("/search", response_model=list[SearchProfileResponse])
def list_search_profiles(request: Request) -> list[SearchProfileResponse]:
    return [search_response(profile) for profile in _service(request).list_search_profiles()]


@router.get("/search/default", response_model=SearchProfileResponse | None)
def get_default_search_profile(request: Request) -> SearchProfileResponse | None:
    profile = _service(request).get_default_search_profile()
    return None if profile is None else search_response(profile)


@router.get("/search/{profile_id}", response_model=SearchProfileResponse)
def get_search_profile(profile_id: str, request: Request) -> SearchProfileResponse:
    profile = _service(request).get_search_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Search Profile not found.")
    return search_response(profile)


@router.post("/search", response_model=SearchProfileResponse, status_code=201)
def create_search_profile(payload: SearchProfilePayload, request: Request) -> SearchProfileResponse:
    try:
        return search_response(_service(request).create_search_profile(search_from_payload(payload)))
    except (ProfileValidationError, SearchProfileConflictError) as error:
        raise _error(error) from error


@router.put("/search/{profile_id}", response_model=SearchProfileResponse)
def revise_search_profile(profile_id: str, payload: SearchProfilePayload, request: Request) -> SearchProfileResponse:
    try:
        return search_response(_service(request).revise_search_profile(profile_id, search_from_payload(payload)))
    except (ProfileValidationError, SearchProfileConflictError, SearchProfileNotFoundError) as error:
        raise _error(error) from error


@router.post("/search/{profile_id}/default", response_model=SearchProfileResponse)
def set_default_search_profile(profile_id: str, request: Request) -> SearchProfileResponse:
    try:
        return search_response(_service(request).set_default_search_profile(profile_id))
    except SearchProfileNotFoundError as error:
        raise _error(error) from error


@router.delete("/search/{profile_id}", status_code=204)
def delete_search_profile(profile_id: str, request: Request) -> Response:
    try:
        _service(request).delete_search_profile(profile_id)
    except SearchProfileNotFoundError as error:
        raise _error(error) from error
    return Response(status_code=204)
