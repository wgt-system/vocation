from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vocation.api.criteria_routes import router as criteria_router
from vocation.api.import_routes import router as import_router
from vocation.api.opportunity_routes import router as opportunity_router
from vocation.api.prompt_routes import router as prompt_router
from vocation.application.criteria import CriteriaService
from vocation.application.imports import ImportService
from vocation.application.opportunities import OpportunityQueryService
from vocation.application.personal_triage import PersonalTriageService
from vocation.application.prompts import PromptService
from vocation.config import Settings, get_settings
from vocation.infrastructure.bundle_repository import SqlAlchemyImportRepository
from vocation.infrastructure.database import Database
from vocation.infrastructure.opportunity_queries import SqlAlchemyOpportunityReadRepository
from vocation.infrastructure.personal_triage_repository import SqlAlchemyPersonalTriageRepository
from vocation.infrastructure.repositories import (
    SqlAlchemyCriteriaRepository,
    SqlAlchemyPromptRunRepository,
)


def create_app(settings: Settings | None = None, *, run_migrations: bool = True) -> FastAPI:
    settings = settings or get_settings()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if run_migrations:
            database.migrate()
        yield
        database.dispose()

    app = FastAPI(title="Vocation", version="0.1.0", lifespan=lifespan)
    app.state.database = database
    app.state.settings = settings
    criteria_repository = SqlAlchemyCriteriaRepository(database.session_factory)
    app.state.criteria_service = CriteriaService(criteria_repository)
    app.state.prompt_service = PromptService(
        app.state.criteria_service,
        SqlAlchemyPromptRunRepository(database.session_factory),
        settings.initial_prompt_path,
        settings.output_contract_path,
    )
    app.state.import_service = ImportService(
        SqlAlchemyImportRepository(database.session_factory),
        app.state.criteria_service,
        settings.schema_path,
    )
    app.state.personal_triage_service = PersonalTriageService(
        SqlAlchemyPersonalTriageRepository(database.session_factory), criteria_repository
    )
    app.state.opportunity_service = OpportunityQueryService(SqlAlchemyOpportunityReadRepository(database.session_factory))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "vocation"}

    app.include_router(criteria_router)
    app.include_router(prompt_router)
    app.include_router(import_router)
    app.include_router(opportunity_router)

    frontend_dist: Path = settings.frontend_dist
    if frontend_dist.exists():
        assets = frontend_dist / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str) -> FileResponse:
            candidate = frontend_dist / path
            if path and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


app = create_app()
