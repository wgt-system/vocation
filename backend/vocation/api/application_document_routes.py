from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile, status

from vocation.api.schemas import ApplicationDocumentResponse
from vocation.application.application_documents import (
    ApplicationDocumentConflictError,
    ApplicationDocumentNotFoundError,
    ApplicationDocumentPayloadConflictError,
    ApplicationDocumentPayloadNotFoundError,
    ApplicationDocumentService,
    ApplicationMaterialRevisionNotFoundError,
)
from vocation.domain.application_documents import (
    ApplicationDocument,
    ApplicationDocumentError,
    ApplicationDocumentIntegrityError,
)

router = APIRouter(tags=["application-documents"])


def _service(request: Request) -> ApplicationDocumentService:
    return request.app.state.application_document_service


def _response(document: ApplicationDocument) -> ApplicationDocumentResponse:
    return ApplicationDocumentResponse(
        id=document.id,
        material_id=document.material_id,
        material_revision=document.material_revision,
        original_filename=document.original_filename,
        media_type=document.media_type,
        byte_size=document.byte_size,
        sha256=document.sha256,
        created_at=document.created_at,
    )


def _raise_error(error: Exception) -> None:
    if isinstance(error, (ApplicationDocumentIntegrityError, ApplicationDocumentPayloadNotFoundError)):
        raise HTTPException(status_code=500, detail="Application Document content integrity validation failed.") from error
    if isinstance(error, ApplicationDocumentPayloadConflictError):
        raise HTTPException(status_code=500, detail="Application Document content could not be stored.") from error
    if isinstance(error, (ApplicationDocumentNotFoundError, ApplicationMaterialRevisionNotFoundError)):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, ApplicationDocumentConflictError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, ApplicationDocumentError):
        raise HTTPException(status_code=422, detail=str(error)) from error
    raise error


@router.get(
    "/api/application-materials/{material_id}/revisions/{material_revision}/document",
    response_model=ApplicationDocumentResponse,
)
def get_for_material_revision(material_id: str, material_revision: int, request: Request) -> ApplicationDocumentResponse:
    try:
        document = _service(request).get_for_material_revision(material_id, material_revision)
    except (ApplicationDocumentIntegrityError, ApplicationDocumentPayloadNotFoundError) as error:
        _raise_error(error)
    if document is None:
        raise HTTPException(status_code=404, detail="No Application Document is attached to this material revision.")
    return _response(document)


@router.post(
    "/api/application-materials/{material_id}/revisions/{material_revision}/document",
    response_model=ApplicationDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def attach_document(
    material_id: str,
    material_revision: int,
    request: Request,
    file: Annotated[UploadFile, File()],
) -> ApplicationDocumentResponse:
    if not file.filename:
        raise HTTPException(status_code=422, detail="Uploaded file requires a filename.")
    payload = await file.read()
    try:
        document = _service(request).attach_document(
            material_id,
            material_revision,
            file.filename,
            file.content_type or "",
            payload,
        )
    except (
        ApplicationDocumentConflictError,
        ApplicationDocumentError,
        ApplicationDocumentPayloadConflictError,
        ApplicationMaterialRevisionNotFoundError,
    ) as error:
        _raise_error(error)
    return _response(document)


@router.get("/api/application-documents/{document_id}", response_model=ApplicationDocumentResponse)
def get_document(document_id: str, request: Request) -> ApplicationDocumentResponse:
    try:
        document = _service(request).get(document_id)
    except (ApplicationDocumentIntegrityError, ApplicationDocumentPayloadNotFoundError) as error:
        _raise_error(error)
    if document is None:
        raise HTTPException(status_code=404, detail=f"Application Document '{document_id}' does not exist.")
    return _response(document)


@router.get("/api/application-documents/{document_id}/content", response_class=Response)
def get_content(document_id: str, request: Request) -> Response:
    try:
        document = _service(request).get(document_id)
        if document is None:
            raise ApplicationDocumentNotFoundError(document_id)
        payload = _service(request).read_payload(document_id)
    except (
        ApplicationDocumentIntegrityError,
        ApplicationDocumentNotFoundError,
        ApplicationDocumentPayloadNotFoundError,
    ) as error:
        _raise_error(error)
    return Response(content=payload, media_type=document.media_type)
