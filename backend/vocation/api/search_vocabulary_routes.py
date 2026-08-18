from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field

from vocation.application.search_vocabulary import SearchVocabularyService
from vocation.domain.search_vocabulary import SearchVocabularyEntry, SearchVocabularyValidationError

router = APIRouter(prefix="/api/search-vocabularies", tags=["search-vocabularies"])
VocabularyKind = Literal["role", "technology", "industry", "seniority", "employment_type"]


class SearchVocabularyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: VocabularyKind
    label: str
    aliases: list[str]
    group: str | None
    is_active: bool
    is_custom: bool


class CreateSearchVocabularyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: VocabularyKind
    label: str = Field(min_length=1, max_length=160)
    aliases: list[str] = Field(default_factory=list)
    group: str | None = Field(default=None, max_length=120)


class UpdateSearchVocabularyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str | None = Field(default=None, min_length=1, max_length=160)
    aliases: list[str] | None = None
    group: str | None = Field(default=None, max_length=120)
    is_active: bool | None = None


def _service(request: Request) -> SearchVocabularyService:
    return request.app.state.search_vocabulary_service


def _response(entry: SearchVocabularyEntry) -> SearchVocabularyResponse:
    return SearchVocabularyResponse(
        id=entry.id,
        kind=entry.kind,
        label=entry.label,
        aliases=list(entry.aliases),
        group=entry.group,
        is_active=entry.is_active,
        is_custom=entry.is_custom,
    )


@router.get("", response_model=list[SearchVocabularyResponse])
def list_search_vocabularies(
    request: Request,
    kind: VocabularyKind | None = None,
    q: Annotated[str, Query(max_length=160)] = "",
    include_inactive: bool = False,
) -> list[SearchVocabularyResponse]:
    try:
        entries = _service(request).list_entries(
            kind=kind,
            include_inactive=include_inactive,
            query=q,
        )
    except SearchVocabularyValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return [_response(entry) for entry in entries]


@router.post("/custom", response_model=SearchVocabularyResponse, status_code=status.HTTP_201_CREATED)
def create_custom_search_vocabulary(
    request: Request,
    payload: CreateSearchVocabularyRequest,
) -> SearchVocabularyResponse:
    try:
        entry = _service(request).create_custom(
            kind=payload.kind,
            label=payload.label,
            aliases=tuple(payload.aliases),
            group=payload.group,
        )
    except SearchVocabularyValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return _response(entry)


@router.patch("/{entry_id}", response_model=SearchVocabularyResponse)
def update_search_vocabulary(
    entry_id: str,
    request: Request,
    payload: UpdateSearchVocabularyRequest,
) -> SearchVocabularyResponse:
    fields_set = payload.model_fields_set
    try:
        entry = _service(request).update(
            entry_id,
            label=payload.label,
            aliases=None if payload.aliases is None else tuple(payload.aliases),
            group=payload.group,
            group_supplied="group" in fields_set,
            is_active=payload.is_active,
        )
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except SearchVocabularyValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return _response(entry)
