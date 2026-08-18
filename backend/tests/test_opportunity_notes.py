from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from tests.test_imports import import_bundle, valid_bundle
from tests.test_profiles import search_payload
from vocation.api.app import create_app
from vocation.config import get_settings

ROOT = Path(__file__).resolve().parents[2]


def opportunity_id(client) -> str:
    return client.get("/api/opportunities").json()[0]["id"]


def test_opportunity_note_create_update_and_clear(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)

    assert client.get(f"/api/opportunities/{oid}/note").json() is None

    created = client.put(
        f"/api/opportunities/{oid}/note",
        json={"content": "  Strong role, verify team size.  "},
    )
    assert created.status_code == 200
    assert created.json()["opportunity_id"] == oid
    assert created.json()["content"] == "Strong role, verify team size."
    assert created.json()["updated_at"]

    updated = client.put(
        f"/api/opportunities/{oid}/note",
        json={"content": "Ask about onboarding."},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == "Ask about onboarding."
    assert client.get(f"/api/opportunities/{oid}/note").json()["content"] == "Ask about onboarding."

    cleared = client.put(f"/api/opportunities/{oid}/note", json={"content": "   \n  "})
    assert cleared.status_code == 200
    assert cleared.json() is None
    assert client.get(f"/api/opportunities/{oid}/note").json() is None


def test_opportunity_note_requires_existing_opportunity(client) -> None:
    missing = client.get("/api/opportunities/missing/note")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Opportunity 'missing' does not exist."
    assert client.put("/api/opportunities/missing/note", json={"content": "note"}).status_code == 404


def test_opportunity_note_does_not_affect_fit(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    profile = client.post("/api/profiles/search", json=search_payload())
    assert profile.status_code == 201
    profile_id = profile.json()["id"]

    before = client.get(f"/api/opportunities/{oid}/fit?search_profile_id={profile_id}")
    assert before.status_code == 200
    assert client.put(f"/api/opportunities/{oid}/note", json={"content": "Private analysis only."}).status_code == 200
    after = client.get(f"/api/opportunities/{oid}/fit?search_profile_id={profile_id}")
    assert after.status_code == 200
    assert after.json() == before.json()


def test_repeated_research_import_does_not_overwrite_opportunity_note(client) -> None:
    bundle = valid_bundle()
    assert import_bundle(client, bundle).status_code == 200
    oid = opportunity_id(client)
    assert client.put(f"/api/opportunities/{oid}/note", json={"content": "Keep this private note."}).status_code == 200

    assert import_bundle(client, bundle).status_code == 200
    note = client.get(f"/api/opportunities/{oid}/note").json()
    assert note["content"] == "Keep this private note."


def test_update_import_does_not_overwrite_opportunity_note(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    assert client.put(f"/api/opportunities/{oid}/note", json={"content": "Personal follow-up."}).status_code == 200

    generated = client.post(
        "/api/prompts/update",
        json={"mode": "full_update", "as_of_date": "2026-08-18"},
    )
    assert generated.status_code == 200
    context = json.loads(
        generated.json()["prompt_text"].split("## Prompt Context\n", 1)[1].split("\n\n## Active Assessment Criteria", 1)[0]
    )
    bundle = json.loads((ROOT / "examples" / "updates" / "full-update-valid.json").read_text(encoding="utf-8"))
    bundle["prompt_context_ref"] = generated.json()["prompt_context_ref"]
    bundle["research_scope"] = context["research_scope"]
    applied = client.post("/api/imports/text", json={"content": json.dumps(bundle)})
    assert applied.status_code == 200
    assert applied.json()["status"] == "applied"

    note = client.get(f"/api/opportunities/{oid}/note").json()
    assert note["content"] == "Personal follow-up."


def test_opportunity_note_survives_application_restart(tmp_path: Path) -> None:
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{(tmp_path / 'notes.db').as_posix()}",
        frontend_dist=tmp_path / "no-frontend",
    )
    with TestClient(create_app(settings)) as client:
        assert import_bundle(client, valid_bundle()).status_code == 200
        oid = opportunity_id(client)
        saved = client.put(f"/api/opportunities/{oid}/note", json={"content": "Persistent private note."})
        assert saved.status_code == 200

    with TestClient(create_app(settings)) as client:
        note = client.get(f"/api/opportunities/{oid}/note")
        assert note.status_code == 200
        assert note.json()["content"] == "Persistent private note."
