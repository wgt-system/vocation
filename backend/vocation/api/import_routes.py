from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, UploadFile

from vocation.api.schemas import ImportIssueResponse, ImportReportResponse, ImportTextPayload
from vocation.application.imports import MAX_IMPORT_BYTES, ImportService
from vocation.domain.research_bundle import ImportReport

router = APIRouter(prefix="/api/imports", tags=["research imports"])


def _response(report: ImportReport) -> ImportReportResponse:
    return ImportReportResponse(
        import_id=report.import_id,
        status=report.status,
        bundle_id=report.bundle_id,
        fingerprint=report.fingerprint,
        counts=report.counts,
        warnings=report.warnings,
        issues=[ImportIssueResponse(**issue.__dict__) for issue in report.issues],
        duplicate_of_import_id=report.duplicate_of_import_id,
    )


@router.post("/text", response_model=ImportReportResponse)
def import_text(payload: ImportTextPayload, request: Request) -> ImportReportResponse:
    service: ImportService = request.app.state.import_service
    return _response(service.import_text(payload.content))


@router.post("/file", response_model=ImportReportResponse)
async def import_file(file: UploadFile, request: Request) -> ImportReportResponse:
    content = await file.read(MAX_IMPORT_BYTES + 1)
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="Research Bundle file is too large.")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=422, detail="Research Bundle must be UTF-8 JSON.") from error
    service: ImportService = request.app.state.import_service
    return _response(service.import_text(text))


@router.get("/{import_id}", response_model=ImportReportResponse)
def get_import_report(import_id: str, request: Request) -> ImportReportResponse:
    service: ImportService = request.app.state.import_service
    report = service.get_report(import_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Import report not found.")
    return _response(report)
