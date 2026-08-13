from __future__ import annotations

from datetime import UTC, datetime
from itertools import count
from pathlib import Path

import pytest
from sqlalchemy import text
from tests.test_migrations import migrate, seed_application_document_data, seed_v020_data
from vocation.application.application_documents import (
    ApplicationDocumentConflictError,
    ApplicationDocumentNotFoundError,
    ApplicationDocumentPayloadNotFoundError,
    ApplicationDocumentService,
    ApplicationMaterialRevisionNotFoundError,
)
from vocation.domain.application_documents import ApplicationDocumentIntegrityError
from vocation.infrastructure.application_document_repository import SqlAlchemyApplicationDocumentRepository
from vocation.infrastructure.database import Database

OCCURRED_AT = datetime(2026, 8, 13, 12, tzinfo=UTC)


class InMemoryDocumentStore:
    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}
        self.fail_write = False
        self.fail_read = False

    def write(self, storage_ref: str, payload: bytes) -> None:
        if self.fail_write:
            raise RuntimeError("write failed")
        self.payloads[storage_ref] = payload

    def read(self, storage_ref: str) -> bytes:
        if self.fail_read:
            raise RuntimeError("read failed")
        if storage_ref not in self.payloads:
            raise ApplicationDocumentPayloadNotFoundError(storage_ref)
        return self.payloads[storage_ref]


def make_service(database: Path):
    migrate(database, "head")
    seed_v020_data(database)
    seed_application_document_data(database)
    db = Database(f"sqlite:///{database.as_posix()}")
    repository = SqlAlchemyApplicationDocumentRepository(db.session_factory)
    store = InMemoryDocumentStore()
    document_counter = count(1)
    storage_counter = count(1)
    service = ApplicationDocumentService(
        repository,
        store,
        ref_factory=lambda: f"document-{next(document_counter)}",
        storage_ref_factory=lambda: f"opaque-storage-{next(storage_counter)}",
        clock=lambda: OCCURRED_AT,
    )
    return db, repository, store, service


def test_attach_writes_and_persists_for_exact_material_revision(tmp_path: Path) -> None:
    db, repository, store, service = make_service(tmp_path / "attach.db")

    document = service.attach_document("material-document", 1, " Resume.pdf ", "application/pdf", b"resume bytes")

    assert document.material_id == "material-document"
    assert document.material_revision == 1
    assert document.original_filename == "Resume.pdf"
    stored = repository.get(document.id)
    assert stored is not None
    assert stored.storage_ref in store.payloads
    assert stored.document == document
    assert not hasattr(document, "storage_ref")
    db.dispose()


def test_historical_revision_and_independent_equal_digest_documents_are_supported(tmp_path: Path) -> None:
    db, repository, _store, service = make_service(tmp_path / "revisions.db")

    first = service.attach_document("material-document", 1, "Resume.pdf", "application/pdf", b"same bytes")
    second = service.attach_document("material-document", 2, "Resume revised.pdf", "application/pdf", b"same bytes")

    assert first.id != second.id
    assert first.sha256 == second.sha256
    assert repository.get_for_material_revision("material-document", 1).document == first  # type: ignore[union-attr]
    assert repository.get_for_material_revision("material-document", 2).document == second  # type: ignore[union-attr]
    db.dispose()


def test_second_document_for_one_material_revision_is_rejected(tmp_path: Path) -> None:
    db, repository, _store, service = make_service(tmp_path / "duplicate.db")

    service.attach_document("material-document", 1, "Resume.pdf", "application/pdf", b"one")
    with pytest.raises(ApplicationDocumentConflictError):
        service.attach_document("material-document", 1, "Other.pdf", "application/pdf", b"two")
    assert repository.get_for_material_revision("material-document", 1) is not None
    db.dispose()


def test_get_and_read_payload_round_trip_and_integrity_failures(tmp_path: Path) -> None:
    db, repository, store, service = make_service(tmp_path / "integrity.db")
    document = service.attach_document("material-document", 1, "Resume.pdf", "text/plain", b"exact payload")

    assert service.get(document.id) == document
    assert service.get_for_material_revision("material-document", 1) == document
    assert service.read_payload(document.id) == b"exact payload"

    stored = repository.get(document.id)
    assert stored is not None
    del store.payloads[stored.storage_ref]
    with pytest.raises(ApplicationDocumentIntegrityError):
        service.get(document.id)
    store.payloads[stored.storage_ref] = b"exact payloaD"  # same length, different digest
    with pytest.raises(ApplicationDocumentIntegrityError):
        service.read_payload(document.id)
    with pytest.raises(ApplicationDocumentNotFoundError):
        service.read_payload("missing")
    db.dispose()


def test_store_failures_leave_no_document_metadata(tmp_path: Path) -> None:
    db, repository, store, service = make_service(tmp_path / "store-failure.db")
    store.fail_write = True
    with pytest.raises(RuntimeError):
        service.attach_document("material-document", 1, "Resume.pdf", "application/pdf", b"payload")
    assert repository.get_for_material_revision("material-document", 1) is None

    store.fail_write = False
    store.fail_read = True
    with pytest.raises(RuntimeError):
        service.attach_document("material-document", 1, "Resume.pdf", "application/pdf", b"payload")
    assert repository.get_for_material_revision("material-document", 1) is None
    db.dispose()


def test_missing_material_revision_is_rejected(tmp_path: Path) -> None:
    db, _repository, _store, service = make_service(tmp_path / "missing-revision.db")

    with pytest.raises(ApplicationMaterialRevisionNotFoundError):
        service.attach_document("material-document", 99, "Resume.pdf", "application/pdf", b"payload")
    db.dispose()


def test_documents_do_not_change_case_lifecycle_or_tracking_status(tmp_path: Path) -> None:
    db, _repository, _store, service = make_service(tmp_path / "state.db")

    service.attach_document("material-document", 1, "Resume.pdf", "application/pdf", b"payload")
    with db.engine.connect() as connection:
        assert connection.scalar(text("SELECT lifecycle FROM application_cases WHERE id = 'case-document'")) == "draft"
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
    db.dispose()
