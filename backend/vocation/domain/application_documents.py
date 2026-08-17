from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Literal, cast

from vocation.domain.application_cases import ApplicationMaterial

ApplicationDocumentMediaType = Literal["application/pdf", "text/plain", "text/markdown"]

_MEDIA_TYPES = frozenset({"application/pdf", "text/plain", "text/markdown"})


class ApplicationDocumentError(ValueError):
    """Base error for invalid Application Document values."""


class ApplicationDocumentIntegrityError(ApplicationDocumentError):
    """The document payload does not match its stored metadata."""


@dataclass(frozen=True)
class ApplicationDocument:
    id: str
    material_id: str
    material_revision: int
    original_filename: str
    media_type: ApplicationDocumentMediaType
    byte_size: int
    sha256: str
    created_at: datetime


def _require_nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ApplicationDocumentError(f"{label} must be nonempty.")
    return value.strip()


def _media_type(value: str) -> ApplicationDocumentMediaType:
    if value not in _MEDIA_TYPES:
        raise ApplicationDocumentError(f"Unsupported application document media type: {value!r}.")
    return cast(ApplicationDocumentMediaType, value)


def create_application_document(
    document_id: str,
    material: ApplicationMaterial,
    original_filename: str,
    media_type: str,
    payload: bytes,
    occurred_at: datetime,
) -> ApplicationDocument:
    document_id = _require_nonempty(document_id, "Application Document ID")
    if not isinstance(material, ApplicationMaterial):
        raise ApplicationDocumentError("Material must be an ApplicationMaterial.")
    filename = _require_nonempty(original_filename, "Original filename")
    if not isinstance(payload, bytes):
        raise ApplicationDocumentError("Application Document payload must be bytes.")
    digest = sha256(payload).hexdigest()
    return ApplicationDocument(
        id=document_id,
        material_id=material.id,
        material_revision=material.revision,
        original_filename=filename,
        media_type=_media_type(media_type),
        byte_size=len(payload),
        sha256=digest,
        created_at=occurred_at,
    )


def validate_application_document_integrity(document: ApplicationDocument, payload: bytes) -> None:
    if not isinstance(payload, bytes):
        raise ApplicationDocumentIntegrityError("Application Document payload must be bytes.")
    actual_size = len(payload)
    actual_digest = sha256(payload).hexdigest()
    if document.byte_size != actual_size or document.sha256 != actual_digest:
        raise ApplicationDocumentIntegrityError("Application Document payload does not match its metadata.")
