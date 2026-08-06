from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import GeneratedPromptResponse, InitialPromptPayload
from vocation.application.prompts import PromptService


router = APIRouter(prefix="/api/prompts", tags=["research prompts"])


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
