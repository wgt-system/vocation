from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, UploadFile

from vocation.api.schemas import AvailabilityImportReportResponse, AvailabilityImportTextPayload, ImportIssueResponse
from vocation.application.availability_imports import MAX_IMPORT_BYTES, AvailabilityImportService
from vocation.domain.research_bundle import ImportReport

router = APIRouter(prefix="/api/availability", tags=["availability"])


def _response(report: ImportReport) -> AvailabilityImportReportResponse:
    return AvailabilityImportReportResponse(
        import_id=report.import_id,
        import_kind="availability_check",
        status=report.status,
        bundle_id=report.bundle_id,
        fingerprint=report.fingerprint,
        counts=report.counts,
        warnings=report.warnings,
        issues=[
            ImportIssueResponse(severity=issue.severity, code=issue.code, path=issue.path, message=issue.message) for issue in report.issues
        ],
        duplicate_of_import_id=report.duplicate_of_import_id,
        bundle_version=report.bundle_version,
        prompt_context_ref=report.prompt_context_ref,
    )


@router.post("/imports/text", response_model=AvailabilityImportReportResponse)
def import_text(payload: AvailabilityImportTextPayload, request: Request) -> AvailabilityImportReportResponse:
    service: AvailabilityImportService = request.app.state.availability_import_service
    return _response(service.import_text(payload.content))


@router.post("/imports/file", response_model=AvailabilityImportReportResponse)
async def import_file(file: UploadFile, request: Request) -> AvailabilityImportReportResponse:
    content = await file.read(MAX_IMPORT_BYTES + 1)
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="Availability Check file is too large.")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=422, detail="Availability Check must be UTF-8 JSON.") from error
    service: AvailabilityImportService = request.app.state.availability_import_service
    return _response(service.import_text(text))


@router.get("/imports/{import_id}", response_model=AvailabilityImportReportResponse)
def get_import_report(import_id: str, request: Request) -> AvailabilityImportReportResponse:
    service: AvailabilityImportService = request.app.state.availability_import_service
    report = service.get_report(import_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Availability import report not found.")
    return _response(report)
