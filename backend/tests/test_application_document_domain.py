from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest
from vocation.domain.application_cases import create_application_material
from vocation.domain.application_documents import (
    ApplicationDocument,
    ApplicationDocumentError,
    ApplicationDocumentIntegrityError,
    create_application_document,
    validate_application_document_integrity,
)

OCCURRED_AT = datetime(2026, 8, 13, 12, tzinfo=UTC)


def make_material():
    return create_application_material("material-1", "case-1", "cv", "Resume", OCCURRED_AT)


def make_document(media_type: str = "application/pdf", payload: bytes = b"document bytes") -> ApplicationDocument:
    return create_application_document("document-1", make_material(), " Resume.pdf ", media_type, payload, OCCURRED_AT)


def test_creation_derives_material_identity_and_metadata_from_payload() -> None:
    document = make_document()

    assert document.material_id == "material-1"
    assert document.material_revision == 1
    assert document.original_filename == "Resume.pdf"
    assert document.byte_size == 14
    assert document.sha256 == "5a855430e6b6a41750a0928768920a774a02f00d02d79d2880a4204a2f1f22f5"


def test_document_is_immutable() -> None:
    document = make_document()

    with pytest.raises(FrozenInstanceError):
        document.original_filename = "changed.pdf"  # type: ignore[misc]


@pytest.mark.parametrize("media_type", ["application/pdf", "text/plain", "text/markdown"])
def test_allowed_media_types_are_accepted(media_type: str) -> None:
    assert make_document(media_type).media_type == media_type


def test_unsupported_media_type_rejects() -> None:
    with pytest.raises(ApplicationDocumentError):
        make_document("application/octet-stream")


def test_blank_document_id_and_filename_reject() -> None:
    material = make_material()
    with pytest.raises(ApplicationDocumentError):
        create_application_document(" ", material, "Resume.pdf", "application/pdf", b"x", OCCURRED_AT)
    with pytest.raises(ApplicationDocumentError):
        create_application_document("document-1", material, "  ", "application/pdf", b"x", OCCURRED_AT)


def test_non_bytes_payload_rejects() -> None:
    with pytest.raises(ApplicationDocumentError):
        create_application_document("document-1", make_material(), "Resume.pdf", "application/pdf", "not bytes", OCCURRED_AT)  # type: ignore[arg-type]


def test_integrity_accepts_original_payload() -> None:
    document = make_document(payload=b"original")

    validate_application_document_integrity(document, b"original")


def test_integrity_rejects_different_content() -> None:
    document = make_document(payload=b"original")

    with pytest.raises(ApplicationDocumentIntegrityError):
        validate_application_document_integrity(document, b"changed")


def test_integrity_rejects_same_size_with_different_digest() -> None:
    document = make_document(payload=b"abc")

    with pytest.raises(ApplicationDocumentIntegrityError):
        validate_application_document_integrity(document, b"xyz")
