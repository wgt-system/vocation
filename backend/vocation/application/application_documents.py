from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from vocation.domain.application_cases import ApplicationMaterial
from vocation.domain.application_documents import (
    ApplicationDocument,
    ApplicationDocumentError,
    ApplicationDocumentIntegrityError,
    create_application_document,
    validate_application_document_integrity,
)


class ApplicationDocumentStore(Protocol):
    def write(self, storage_ref: str, payload: bytes) -> None: ...

    def read(self, storage_ref: str) -> bytes: ...


class ApplicationDocumentPayloadNotFoundError(ApplicationDocumentError):
    """The referenced document bytes are not available from the store."""


class ApplicationDocumentPayloadConflictError(ApplicationDocumentError):
    """The referenced storage location already contains immutable bytes."""


class ApplicationDocumentNotFoundError(LookupError):
    """The requested document metadata does not exist."""


class ApplicationMaterialRevisionNotFoundError(LookupError):
    """The requested immutable material revision does not exist."""


class ApplicationDocumentConflictError(ValueError):
    """A document already exists for the requested material revision."""


@dataclass(frozen=True)
class StoredApplicationDocument:
    document: ApplicationDocument
    storage_ref: str


class ApplicationDocumentRepository(Protocol):
    def get(self, document_id: str) -> StoredApplicationDocument | None: ...

    def get_for_material_revision(self, material_id: str, material_revision: int) -> StoredApplicationDocument | None: ...

    def get_material_revision(self, material_id: str, material_revision: int) -> ApplicationMaterial | None: ...

    def create(self, document: ApplicationDocument, storage_ref: str) -> ApplicationDocument: ...


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ApplicationDocumentService:
    def __init__(
        self,
        repository: ApplicationDocumentRepository,
        store: ApplicationDocumentStore,
        ref_factory: Callable[[], str] | None = None,
        storage_ref_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.store = store
        self.ref_factory = ref_factory or (lambda: str(uuid4()))
        self.storage_ref_factory = storage_ref_factory or (lambda: str(uuid4()))
        self.clock = clock or _utc_now

    def attach_document(
        self,
        material_id: str,
        material_revision: int,
        original_filename: str,
        media_type: str,
        payload: bytes,
    ) -> ApplicationDocument:
        material = self.repository.get_material_revision(material_id, material_revision)
        if material is None:
            raise ApplicationMaterialRevisionNotFoundError(material_id)
        if self.repository.get_for_material_revision(material_id, material_revision) is not None:
            raise ApplicationDocumentConflictError("An Application Document already exists for this material revision.")
        document = create_application_document(self.ref_factory(), material, original_filename, media_type, payload, self.clock())
        storage_ref = self.storage_ref_factory()
        self.store.write(storage_ref, payload)
        try:
            stored_payload = self.store.read(storage_ref)
        except ApplicationDocumentPayloadNotFoundError as error:
            raise ApplicationDocumentIntegrityError("Application Document payload is missing.") from error
        validate_application_document_integrity(document, stored_payload)
        return self.repository.create(document, storage_ref)

    def get(self, document_id: str) -> ApplicationDocument | None:
        stored = self.repository.get(document_id)
        if stored is None:
            return None
        return self._read_stored(stored)

    def get_for_material_revision(self, material_id: str, material_revision: int) -> ApplicationDocument | None:
        stored = self.repository.get_for_material_revision(material_id, material_revision)
        if stored is None:
            return None
        return self._read_stored(stored)

    def read_payload(self, document_id: str) -> bytes:
        stored = self.repository.get(document_id)
        if stored is None:
            raise ApplicationDocumentNotFoundError(document_id)
        try:
            payload = self.store.read(stored.storage_ref)
        except ApplicationDocumentPayloadNotFoundError as error:
            raise ApplicationDocumentIntegrityError("Application Document payload is missing.") from error
        validate_application_document_integrity(stored.document, payload)
        return payload

    def _read_stored(self, stored: StoredApplicationDocument) -> ApplicationDocument:
        try:
            payload = self.store.read(stored.storage_ref)
        except ApplicationDocumentPayloadNotFoundError as error:
            raise ApplicationDocumentIntegrityError("Application Document payload is missing.") from error
        validate_application_document_integrity(stored.document, payload)
        return stored.document
