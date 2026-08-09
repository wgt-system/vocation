from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    GeneratedPromptResponse,
    GeneratedUpdatePromptResponse,
    InitialPromptPayload,
    UpdatePromptOptionsResponse,
    UpdatePromptPayload,
)
from vocation.application.prompts import PromptService

router = APIRouter(prefix="/api/prompts", tags=["research prompts"])


@router.get("/update-options", response_model=UpdatePromptOptionsResponse)
def update_prompt_options(request: Request) -> UpdatePromptOptionsResponse:
    service: PromptService = request.app.state.prompt_service
    return UpdatePromptOptionsResponse(**service.update_options())


@router.post("/initial", response_model=GeneratedPromptResponse)
def generate_initial_prompt(payload: InitialPromptPayload, request: Request) -> GeneratedPromptResponse:
    service: PromptService = request.app.state.prompt_service
    try:
        generated = service.generate_initial(
            search_profile=payload.search_profile,
            constraints=payload.constraints,
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
