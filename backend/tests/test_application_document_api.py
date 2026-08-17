from __future__ import annotations

import hashlib
import json

from sqlalchemy import text
from tests.test_imports import valid_bundle


def create_material(client, *, kind: str = "cv") -> tuple[str, str]:
    imported = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())})
    assert imported.json()["status"] == "applied"
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    case = client.post(f"/api/opportunities/{opportunity_id}/application-cases").json()
    material = client.post(
        f"/api/application-cases/{case['id']}/materials",
        json={"kind": kind, "display_name": "Test material"},
    ).json()
    return opportunity_id, material["id"]


def attach(client, material_id: str, revision: int, filename: str, payload: bytes, media_type: str):
    return client.post(
        f"/api/application-materials/{material_id}/revisions/{revision}/document",
        files={"file": (filename, payload, media_type)},
    )


def test_attach_pdf_returns_exact_private_metadata(client) -> None:
    _opportunity_id, material_id = create_material(client)
    payload = b"%PDF-test"

    response = attach(client, material_id, 1, "test.pdf", payload, "application/pdf")

    assert response.status_code == 201
    body = response.json()
    assert body["material_id"] == material_id
    assert body["material_revision"] == 1
    assert body["original_filename"] == "test.pdf"
    assert body["media_type"] == "application/pdf"
    assert body["byte_size"] == len(payload)
    assert body["sha256"] == hashlib.sha256(payload).hexdigest()
    assert "storage_ref" not in body
    assert "path" not in body


def test_plain_text_markdown_and_path_looking_filename_are_metadata_only(client, app) -> None:
    _opportunity_id, material_id = create_material(client)
    first = attach(client, material_id, 1, "../private/test.txt", b"test document", "text/plain")
    assert first.status_code == 201
    assert first.json()["original_filename"] == "../private/test.txt"
    assert first.json()["media_type"] == "text/plain"

    client.post(f"/api/application-materials/{material_id}/revisions", json={"display_name": "Revision 2"})
    second = attach(client, material_id, 2, "test.md", b"# test", "text/markdown")
    assert second.status_code == 201
    assert second.json()["media_type"] == "text/markdown"
    assert all(
        item.is_file() and item.parent == app.state.settings.application_document_store_dir
        for item in app.state.settings.application_document_store_dir.iterdir()
    )


def test_metadata_and_content_get_round_trip(client) -> None:
    _opportunity_id, material_id = create_material(client)
    payload = b"test document"
    created = attach(client, material_id, 1, "test.txt", payload, "text/plain").json()

    by_revision = client.get(f"/api/application-materials/{material_id}/revisions/1/document")
    by_id = client.get(f"/api/application-documents/{created['id']}")
    content = client.get(f"/api/application-documents/{created['id']}/content")

    assert by_revision.json() == created
    assert by_id.json() == created
    assert "storage_ref" not in json.dumps(by_revision.json())
    assert "storage_ref" not in json.dumps(by_id.json())
    assert content.content == payload
    assert content.headers["content-type"] == "text/plain; charset=utf-8"


def test_invalid_uploads_conflicts_and_missing_resources_are_mapped(client) -> None:
    _opportunity_id, material_id = create_material(client)

    assert attach(client, material_id, 1, "test.bin", b"bytes", "application/octet-stream").status_code == 422
    assert attach(client, material_id, 99, "test.pdf", b"%PDF-test", "application/pdf").status_code == 404
    assert client.post(f"/api/application-materials/{material_id}/revisions/1/document").status_code == 422
    assert client.get(f"/api/application-materials/{material_id}/revisions/1/document").status_code == 404
    assert client.get("/api/application-documents/missing").status_code == 404
    assert client.get("/api/application-documents/missing/content").status_code == 404

    assert attach(client, material_id, 1, "test.pdf", b"%PDF-test", "application/pdf").status_code == 201
    assert attach(client, material_id, 1, "other.pdf", b"%PDF-other", "application/pdf").status_code == 409


def test_historical_revision_can_receive_document_after_revision_two_exists(client) -> None:
    _opportunity_id, material_id = create_material(client)
    revised = client.post(
        f"/api/application-materials/{material_id}/revisions",
        json={"display_name": "Revision 2"},
    )
    assert revised.json()["revision"] == 2

    historical = attach(client, material_id, 1, "old.pdf", b"%PDF-old", "application/pdf")
    current = attach(client, material_id, 2, "new.pdf", b"%PDF-new", "application/pdf")

    assert historical.status_code == 201
    assert historical.json()["material_revision"] == 1
    assert current.status_code == 201
    assert current.json()["material_revision"] == 2


def physical_payload_path(app, document_id: str):
    with app.state.database.engine.connect() as connection:
        storage_ref = connection.scalar(
            text("SELECT storage_ref FROM application_documents WHERE id = :document_id"),
            {"document_id": document_id},
        )
    return app.state.application_document_service.store._path(storage_ref)


def test_missing_or_corrupted_backing_payload_returns_generic_500(client, app) -> None:
    _opportunity_id, material_id = create_material(client)
    first = attach(client, material_id, 1, "test.txt", b"test document", "text/plain").json()
    missing_path = physical_payload_path(app, first["id"])
    missing_path.unlink()

    missing = client.get(f"/api/application-documents/{first['id']}")
    assert missing.status_code == 500
    assert "storage" not in missing.text.lower()
    assert str(app.state.settings.application_document_store_dir) not in missing.text

    client.post(f"/api/application-materials/{material_id}/revisions", json={"display_name": "Revision 2"})
    second = attach(client, material_id, 2, "test.txt", b"same-size", "text/plain").json()
    corrupt_path = physical_payload_path(app, second["id"])
    corrupt_path.write_bytes(b"different")
    corrupted = client.get(f"/api/application-materials/{material_id}/revisions/2/document")
    assert corrupted.status_code == 500
    assert "storage" not in corrupted.text.lower()
    assert str(corrupt_path) not in corrupted.text


def test_document_operations_preserve_case_and_opportunity_state(client) -> None:
    opportunity_id, material_id = create_material(client)
    before_opportunity = client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"]
    case = client.get(f"/api/opportunities/{opportunity_id}/application-cases").json()[0]

    document = attach(client, material_id, 1, "test.pdf", b"%PDF-test", "application/pdf").json()
    client.get(f"/api/application-documents/{document['id']}")
    client.get(f"/api/application-documents/{document['id']}/content")

    after_case = client.get(f"/api/application-cases/{case['id']}").json()
    assert after_case["lifecycle"] == case["lifecycle"]
    assert after_case["lifecycle_events"] == case["lifecycle_events"]
    assert client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"] == before_opportunity


def test_document_routes_are_internal_openapi_only(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    expected = {
        "/api/application-materials/{material_id}/revisions/{material_revision}/document",
        "/api/application-documents/{document_id}",
        "/api/application-documents/{document_id}/content",
    }
    assert expected <= set(paths)
    assert not any(path.startswith("/published/") and "application-document" in path for path in paths)
