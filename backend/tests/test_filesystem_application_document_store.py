from __future__ import annotations

from pathlib import Path

import pytest
from vocation.application.application_documents import (
    ApplicationDocumentPayloadConflictError,
    ApplicationDocumentPayloadNotFoundError,
)
from vocation.config import REPOSITORY_ROOT, get_settings
from vocation.infrastructure.filesystem_application_document_store import FilesystemApplicationDocumentStore


def test_exact_round_trip_and_missing_root_creation(tmp_path: Path) -> None:
    root = tmp_path / "nested" / "documents"
    store = FilesystemApplicationDocumentStore(root)
    payload = b"private document bytes"

    store.write("document-ref", payload)

    assert root.is_dir()
    assert store.read("document-ref") == payload


def test_storage_ref_maps_deterministically_to_safe_digest_filename(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)
    storage_ref = "../absolute-looking/ref"

    store.write(storage_ref, b"payload")
    first_paths = list(tmp_path.iterdir())
    store_read_path = store._path(storage_ref)

    assert store._path(storage_ref) == store_read_path
    assert len(first_paths) == 1
    assert first_paths[0] == store_read_path
    assert first_paths[0].name != storage_ref
    assert first_paths[0].parent == tmp_path


@pytest.mark.parametrize("storage_ref", ["", "   ", None])
def test_blank_or_non_string_storage_ref_rejects(tmp_path: Path, storage_ref: str | None) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)

    with pytest.raises(ValueError):
        store.write(storage_ref, b"payload")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        store.read(storage_ref)  # type: ignore[arg-type]


def test_non_bytes_payload_rejects(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)

    with pytest.raises(TypeError):
        store.write("document-ref", "payload")  # type: ignore[arg-type]


def test_missing_payload_raises_typed_error(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)

    with pytest.raises(ApplicationDocumentPayloadNotFoundError):
        store.read("missing")


def test_existing_storage_ref_cannot_be_overwritten(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)
    store.write("document-ref", b"original")

    with pytest.raises(ApplicationDocumentPayloadConflictError):
        store.write("document-ref", b"replacement")
    assert store.read("document-ref") == b"original"


def test_failed_duplicate_write_leaves_original_bytes_unchanged(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)
    store.write("document-ref", b"original bytes")

    with pytest.raises(ApplicationDocumentPayloadConflictError):
        store.write("document-ref", b"different bytes")
    assert store.read("document-ref") == b"original bytes"


def test_equal_payloads_under_different_refs_are_independent(tmp_path: Path) -> None:
    store = FilesystemApplicationDocumentStore(tmp_path)
    payload = b"same content"

    store.write("document-one", payload)
    store.write("document-two", payload)

    assert store.read("document-one") == payload
    assert store.read("document-two") == payload
    assert store._path("document-one") != store._path("document-two")
    assert len(list(tmp_path.iterdir())) == 2


def test_environment_override_resolves_through_get_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    configured = tmp_path / "configured-store"
    monkeypatch.setenv("VOCATION_DOCUMENT_STORE_DIR", str(configured))

    assert get_settings().application_document_store_dir == configured


def test_development_default_is_under_data_application_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VOCATION_DOCUMENT_STORE_DIR", raising=False)

    assert get_settings().application_document_store_dir == REPOSITORY_ROOT / "data" / "application-documents"
