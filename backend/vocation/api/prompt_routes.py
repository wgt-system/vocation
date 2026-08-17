from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    AvailabilityPromptPayload,
    GeneratedAvailabilityPromptResponse,
    GeneratedPromptResponse,
    GeneratedUpdatePromptResponse,
    InitialPromptPayload,
    UpdatePromptOptionsResponse,
    UpdatePromptPayload,
)
from vocation.application.availability_prompts import AvailabilityPromptService
from vocation.application.initial_research import InitialResearchService
from vocation.application.prompts import PromptService

router = APIRouter(prefix="/api/prompts", tags=["research prompts"])


@router.get("/update-options", response_model=UpdatePromptOptionsResponse)
def update_prompt_options(request: Request) -> UpdatePromptOptionsResponse:
    service: PromptService = request.app.state.prompt_service
    return UpdatePromptOptionsResponse(**service.update_options())


@router.post("/initial", response_model=GeneratedPromptResponse)
def generate_initial_prompt(payload: InitialPromptPayload, request: Request) -> GeneratedPromptResponse:
    service: InitialResearchService = request.app.state.initial_research_service
    include_candidate_profile = request.query_params.get("include_candidate_profile", "true").lower() not in {
        "false",
        "0",
        "no",
    }
    try:
        generated = service.generate(
            search_profile_selector=payload.search_profile,
            extra_constraints=payload.constraints,
            include_candidate_profile=include_candidate_profile,
            as_of_date=payload.as_of_date.isoformat(),
        )
        return GeneratedPromptResponse(**generated.__dict__)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/update", response_model=GeneratedUpdatePromptResponse)
def generate_update_prompt(payload: UpdatePromptPayload, request: Request) -> GeneratedUpdatePromptResponse:
    service: PromptService = request.app.state.prompt_service
    try:
        generated = service.generate_update(
            mode=payload.mode,
            as_of_date=payload.as_of_date.isoformat(),
            selected_ids=payload.selected_ids,
            gap_requests=[item.model_dump(exclude_none=True) for item in payload.gap_requests],
        )
        return GeneratedUpdatePromptResponse(**generated.__dict__)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/availability-check", response_model=GeneratedAvailabilityPromptResponse)
def generate_availability_prompt(payload: AvailabilityPromptPayload, request: Request) -> GeneratedAvailabilityPromptResponse:
    service: AvailabilityPromptService = request.app.state.availability_prompt_service
    try:
        generated = service.generate(as_of_date=payload.as_of_date.isoformat(), posting_ids=payload.posting_ids)
        return GeneratedAvailabilityPromptResponse(**generated.__dict__)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error