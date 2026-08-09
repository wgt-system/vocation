from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from tests.test_availability import _availability_bundle, _prepare_context
from tests.test_imports import import_bundle, valid_bundle
from vocation.infrastructure.models import PostingModel, PromptRunModel

ROOT = Path(__file__).resolve().parents[2]


def test_availability_prompt_endpoint_persists_exact_context_and_scope(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        posting_id = session.scalar(select(PostingModel)).id
    response = client.post("/api/prompts/availability-check", json={"as_of_date": "2026-08-10", "posting_ids": [posting_id]})
    assert response.status_code == 200
    body = response.json()
    assert body["prompt_type"] == "availability_check"
    assert body["prompt_version"] == "1.0"
    assert body["bundle_kind"] == "availability_check"
    assert body["bundle_version"] == "1.0"
    assert body["research_scope"]["type"] == "availability_check"
    assert len(body["research_scope"]["selected_correlation_refs"]) == 1
    assert (
        json.loads((ROOT / "schemas" / "availability-check-bundle-v1.schema.json").read_text(encoding="utf-8"))["title"]
        in body["prompt_text"]
    )
    with client.app.state.database.session_factory() as session:
        prompt_run = session.get(PromptRunModel, body["prompt_run_id"])
        assert prompt_run is not None
        assert prompt_run.prompt_type == "availability_check"
        assert prompt_run.criteria_snapshot_json == "[]"


def test_availability_prompt_selection_validation(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    assert client.post("/api/prompts/availability-check", json={"as_of_date": "2026-08-10", "posting_ids": []}).status_code == 422
    assert client.post("/api/prompts/availability-check", json={"as_of_date": "2026-08-10", "posting_ids": ["x", "x"]}).status_code == 422
    assert client.post("/api/prompts/availability-check", json={"as_of_date": "2026-08-10", "posting_ids": ["missing"]}).status_code == 422


def test_availability_import_http_boundary_isolated_and_idempotent(client) -> None:
    _prepare_context(client)
    content = json.dumps(_availability_bundle())
    first = client.post("/api/availability/imports/text", json={"content": content})
    assert first.status_code == 200
    assert first.json()["import_kind"] == "availability_check"
    duplicate = client.post("/api/availability/imports/text", json={"content": content})
    assert duplicate.json()["status"] == "duplicate"
    assert client.get(f"/api/availability/imports/{first.json()['import_id']}").json()["status"] == "applied"
    research_id = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()["import_id"]
    assert client.get(f"/api/availability/imports/{research_id}").status_code == 404


def test_availability_file_import_errors_and_read_model_projection(client) -> None:
    _prepare_context(client)
    content = json.dumps(_availability_bundle()).encode()
    applied = client.post("/api/availability/imports/file", files={"file": ("availability.json", content, "application/json")})
    assert applied.status_code == 200
    assert client.post("/api/availability/imports/file", files={"file": ("bad.json", b"\xff", "application/json")}).status_code == 422
    detail = client.get("/api/opportunities").json()[0]
    assert detail["availability"] == "available"
    assert detail["availability_age_days"] >= 0
    opportunity = client.get(f"/api/opportunities/{detail['id']}").json()
    posting = opportunity["postings"][0]
    assert posting["availability"] == "available"
    assert len(posting["availability_history"]) == 1
    assert posting["availability_history"][0]["import_id"] == applied.json()["import_id"]
