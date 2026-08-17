from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from vocation import __version__
from vocation.api.application_case_routes import router as application_case_router
from vocation.api.application_document_routes import router as application_document_router
from vocation.api.availability_routes import router as availability_router
from vocation.api.comparison_routes import router as comparison_router
from vocation.api.criteria_routes import router as criteria_router
from vocation.api.duplicate_case_routes import router as duplicate_case_router
from vocation.api.external_link_routes import router as external_link_router
from vocation.api.group_routes import router as group_router
from vocation.api.import_routes import router as import_router
from vocation.api.map_routes import router as map_router
from vocation.api.opportunity_routes import router as opportunity_router
from vocation.api.profile_routes import router as profile_router
from vocation.api.prompt_routes import router as prompt_router
from vocation.api.published_routes import router as published_router
from vocation.application.application_cases import ApplicationCaseService
from vocation.application.application_documents import ApplicationDocumentService
from vocation.application.availability_imports import AvailabilityImportPlanner, AvailabilityImportService
from vocation.application.availability_prompts import AvailabilityPromptService
from vocation.application.comparison import OpportunityComparisonService
from vocation.application.criteria import CriteriaService
from vocation.application.duplicate_cases import DuplicateCaseService
from vocation.application.external_navigation import ExternalNavigationService
from vocation.application.groups import OpportunityGroupService
from vocation.application.imports import ImportService
from vocation.application.map import MapService
from vocation.application.opportunities import OpportunityQueryService
from vocation.application.personal_triage import PersonalTriageService
from vocation.application.posting_identity import PostingIdentityResolver
from vocation.application.profiles import ProfileService
from vocation.application.prompts import PromptService
from vocation.application.publication import MapProjectionPublicationService, OpportunityOverviewPublicationService
from vocation.application.update_planning import UpdateImportPlanner
from vocation.config import Settings, get_settings
from vocation.infrastructure.application_case_repository import SqlAlchemyApplicationCaseRepository
from vocation.infrastructure.application_document_repository import SqlAlchemyApplicationDocumentRepository
from vocation.infrastructure.availability_repository import SqlAlchemyAvailabilityImportRepository
from vocation.infrastructure.browser_adapter import SystemBrowserAdapter
from vocation.infrastructure.bundle_repository import SqlAlchemyImportRepository
from vocation.infrastructure.comparison_repository import SqlAlchemyComparisonRepository
from vocation.infrastructure.database import Database
from vocation.infrastructure.duplicate_case_repository import SqlAlchemyDuplicateCaseRepository
from vocation.infrastructure.external_link_repository import SqlAlchemyExternalLinkRepository
from vocation.infrastructure.filesystem_application_document_store import FilesystemApplicationDocumentStore
from vocation.infrastructure.group_repository import SqlAlchemyOpportunityGroupRepository
from vocation.infrastructure.map_location_repository import SqlAlchemyMapLocationResolutionRepository
from vocation.infrastructure.opportunity_queries import SqlAlchemyOpportunityReadRepository
from vocation.infrastructure.orientation_geocoder import OrientationGeocoder
from vocation.infrastructure.personal_triage_repository import SqlAlchemyPersonalTriageRepository
from vocation.infrastructure.posting_identity_repository import SqlAlchemyPostingIdentityRepository
from vocation.infrastructure.profile_repository import SqlAlchemyProfileRepository
from vocation.infrastructure.prompt_context_repository import SqlAlchemyPromptContextSnapshotRepository
from vocation.infrastructure.prompt_market_repository import SqlAlchemyPromptMarketRepository
from vocation.infrastructure.publication_repository import (
    SqlAlchemyMapProjectionPublicationRepository,
    SqlAlchemyOpportunityOverviewPublicationRepository,
)
from vocation.infrastructure.repositories import (
    SqlAlchemyCriteriaRepository,
    SqlAlchemyPromptRunRepository,
)
from vocation.infrastructure.update_subject_repository import SqlAlchemyUpdateSubjectRepository


def create_app(settings: Settings | None = None, *, run_migrations: bool = True) -> FastAPI:
    settings = settings or get_settings()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if run_migrations:
            database.migrate()
        try:
            yield
        finally:
            app.state.orientation_geocoder.close()
            database.dispose()

    app = FastAPI(title="Vocation", version=__version__, lifespan=lifespan)
    app.state.database = database
    app.state.settings = settings
    criteria_repository = SqlAlchemyCriteriaRepository(database.session_factory)
    app.state.criteria_service = CriteriaService(criteria_repository)
    app.state.profile_service = ProfileService(SqlAlchemyProfileRepository(database.session_factory))
    app.state.prompt_service = PromptService(
        app.state.criteria_service,
        SqlAlchemyPromptRunRepository(database.session_factory),
        settings.initial_prompt_path,
        settings.output_contract_path,
        SqlAlchemyPromptMarketRepository(database.session_factory),
        settings.update_prompt_dir,
        settings.update_schema_path,
    )
    prompt_market_repository = SqlAlchemyPromptMarketRepository(database.session_factory)
    app.state.availability_prompt_service = AvailabilityPromptService(
        prompt_market_repository,
        SqlAlchemyPromptRunRepository(database.session_factory),
        settings.update_prompt_dir / "availability-check.md",
        settings.schema_path.parent / "availability-check-bundle-v1.schema.json",
    )
    app.state.personal_triage_service = PersonalTriageService(
        SqlAlchemyPersonalTriageRepository(database.session_factory), criteria_repository
    )
    app.state.application_case_service = ApplicationCaseService(SqlAlchemyApplicationCaseRepository(database.session_factory))
    app.state.application_document_service = ApplicationDocumentService(
        SqlAlchemyApplicationDocumentRepository(database.session_factory),
        FilesystemApplicationDocumentStore(settings.application_document_store_dir),
    )
    app.state.opportunity_group_service = OpportunityGroupService(SqlAlchemyOpportunityGroupRepository(database.session_factory))
    app.state.orientation_geocoder = OrientationGeocoder(settings.orientation_base_url)
    app.state.map_service = MapService(SqlAlchemyMapLocationResolutionRepository(database.session_factory), app.state.orientation_geocoder)
    app.state.external_navigation_service = ExternalNavigationService(
        SqlAlchemyExternalLinkRepository(database.session_factory), SystemBrowserAdapter()
    )
    app.state.posting_identity_resolver = PostingIdentityResolver(SqlAlchemyPostingIdentityRepository(database.session_factory))
    app.state.duplicate_case_service = DuplicateCaseService(SqlAlchemyDuplicateCaseRepository(database.session_factory))
    app.state.update_import_planner = UpdateImportPlanner(
        SqlAlchemyPromptContextSnapshotRepository(database.session_factory),
        SqlAlchemyUpdateSubjectRepository(database.session_factory),
        app.state.criteria_service,
        app.state.posting_identity_resolver,
        SqlAlchemyDuplicateCaseRepository(database.session_factory),
    )
    app.state.import_service = ImportService(
        SqlAlchemyImportRepository(database.session_factory),
        app.state.criteria_service,
        settings.schema_path,
        settings.update_schema_path,
        app.state.update_import_planner,
    )
    app.state.availability_import_service = AvailabilityImportService(
        SqlAlchemyAvailabilityImportRepository(database.session_factory),
        AvailabilityImportPlanner(
            SqlAlchemyPromptContextSnapshotRepository(database.session_factory),
            SqlAlchemyUpdateSubjectRepository(database.session_factory),
        ),
        settings.schema_path.parent / "availability-check-bundle-v1.schema.json",
    )
    app.state.opportunity_service = OpportunityQueryService(SqlAlchemyOpportunityReadRepository(database.session_factory))
    app.state.comparison_service = OpportunityComparisonService(SqlAlchemyComparisonRepository(database.session_factory))
    app.state.publication_service = OpportunityOverviewPublicationService(
        SqlAlchemyOpportunityOverviewPublicationRepository(database.session_factory)
    )
    app.state.map_publication_service = MapProjectionPublicationService(
        SqlAlchemyMapProjectionPublicationRepository(database.session_factory)
    )
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
    app.include_router(profile_router)
    app.include_router(application_case_router)
    app.include_router(application_document_router)
    app.include_router(comparison_router)
    app.include_router(duplicate_case_router)
    app.include_router(external_link_router)
    app.include_router(availability_router)
    app.include_router(prompt_router)
    app.include_router(import_router)
    app.include_router(group_router)
    app.include_router(map_router)
    app.include_router(opportunity_router)
    app.include_router(published_router)

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
