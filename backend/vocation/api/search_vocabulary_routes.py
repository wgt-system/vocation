from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, cast
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from vocation.application.search_vocabulary import SearchVocabularyService
from vocation.application.search_vocabulary_prompts import (
    REFRESHABLE_KINDS,
    SearchVocabularyPromptService,
    SearchVocabularyProposal,
)
from vocation.domain.search_vocabulary import SearchVocabularyEntry, SearchVocabularyValidationError

router = APIRouter(prefix="/api/search-vocabularies", tags=["search-vocabularies"])
VocabularyKind = Literal["role", "technology", "industry", "seniority", "employment_type"]
RefreshableVocabularyKind = Literal["role", "technology", "industry"]


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


class SearchVocabularyRefreshPromptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    kinds: list[RefreshableVocabularyKind] = Field(
        default_factory=lambda: list(REFRESHABLE_KINDS)
    )


class SearchVocabularyRefreshPromptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_version: Literal["1.0"]
    as_of_date: date
    kinds: list[RefreshableVocabularyKind]
    prompt_text: str


class SearchVocabularyProposalPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: RefreshableVocabularyKind
    label: str = Field(min_length=1, max_length=160)
    aliases: list[str] = Field(default_factory=list)
    group: str | None = Field(default=None, max_length=120)
    reason: str = Field(min_length=1, max_length=1000)
    source_urls: list[str] = Field(min_length=1)

    @field_validator("source_urls")
    @classmethod
    def validate_source_urls(cls, urls: list[str]) -> list[str]:
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError("Catalog proposal source URLs must be absolute HTTPS URLs.")
        return urls


class SearchVocabularyProposalBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract: Literal["vocation.search-vocabulary-proposals"]
    version: Literal["1.0"]
    as_of_date: date
    proposals: list[SearchVocabularyProposalPayload]


class ReviewedSearchVocabularyProposalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal: SearchVocabularyProposalPayload
    already_known_entry_id: str | None


class ReviewedSearchVocabularyBundleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract: Literal["vocation.search-vocabulary-proposals"]
    version: Literal["1.0"]
    as_of_date: date
    proposals: list[ReviewedSearchVocabularyProposalResponse]


def _service(request: Request) -> SearchVocabularyService:
    return request.app.state.search_vocabulary_service


def _prompt_service(request: Request) -> SearchVocabularyPromptService:
    return request.app.state.search_vocabulary_prompt_service


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    return [_response(entry) for entry in entries]


@router.post(
    "/custom",
    response_model=SearchVocabularyResponse,
    status_code=status.HTTP_201_CREATED,
)
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    return _response(entry)


@router.post(
    "/refresh-prompt", response_model=SearchVocabularyRefreshPromptResponse
)
def generate_search_vocabulary_refresh_prompt(
    request: Request,
    payload: SearchVocabularyRefreshPromptRequest,
) -> SearchVocabularyRefreshPromptResponse:
    try:
        generated = _prompt_service(request).generate(
            as_of_date=payload.as_of_date.isoformat(),
            kinds=tuple(payload.kinds),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    return SearchVocabularyRefreshPromptResponse(
        prompt_version="1.0",
        as_of_date=date.fromisoformat(generated.as_of_date),
        kinds=[cast(RefreshableVocabularyKind, kind) for kind in generated.kinds],
        prompt_text=generated.prompt_text,
    )


@router.post(
    "/proposals/review", response_model=ReviewedSearchVocabularyBundleResponse
)
def review_search_vocabulary_proposals(
    request: Request,
    payload: SearchVocabularyProposalBundle,
) -> ReviewedSearchVocabularyBundleResponse:
    proposals = tuple(
        SearchVocabularyProposal(
            kind=item.kind,
            label=item.label,
            aliases=tuple(item.aliases),
            group=item.group,
            reason=item.reason,
            source_urls=tuple(item.source_urls),
        )
        for item in payload.proposals
    )
    try:
        reviewed = _prompt_service(request).review_proposals(proposals)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    return ReviewedSearchVocabularyBundleResponse(
        contract=payload.contract,
        version=payload.version,
        as_of_date=payload.as_of_date,
        proposals=[
            ReviewedSearchVocabularyProposalResponse(
                proposal=SearchVocabularyProposalPayload(
                    kind=cast(RefreshableVocabularyKind, item.proposal.kind),
                    label=item.proposal.label,
                    aliases=list(item.proposal.aliases),
                    group=item.proposal.group,
                    reason=item.proposal.reason,
                    source_urls=list(item.proposal.source_urls),
                ),
                already_known_entry_id=item.already_known_entry_id,
            )
            for item in reviewed
        ],
    )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except SearchVocabularyValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    return _response(entry)
