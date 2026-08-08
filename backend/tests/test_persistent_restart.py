from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from tests.test_imports import import_bundle, valid_bundle
from vocation.api.app import create_app
from vocation.config import get_settings


def test_personal_triage_state_survives_application_restart(tmp_path: Path) -> None:
    settings = replace(
        get_settings(), database_url=f"sqlite:///{(tmp_path / 'persistent.db').as_posix()}", frontend_dist=tmp_path / "no-frontend"
    )
    with TestClient(create_app(settings)) as client:
        assert import_bundle(client, valid_bundle()).status_code == 200
        opportunity_id = client.get("/api/opportunities").json()[0]["id"]
        first = client.post(
            f"/api/opportunities/{opportunity_id}/assessments/personal",
            json={"criterion_id": "junior_suitability", "value": 4},
        )
        assert first.status_code == 201
        assert (
            client.post(
                f"/api/opportunities/{opportunity_id}/assessments/personal/{first.json()['id']}/revisions",
                json={"value": 5},
            ).status_code
            == 201
        )
        assert client.post(f"/api/opportunities/{opportunity_id}/status", json={"status": "shortlisted"}).status_code == 200
        exclusion = client.post(f"/api/opportunities/{opportunity_id}/exclude", json={"reason": "pause"})
        assert exclusion.status_code == 200
        restore = client.post(f"/api/opportunities/{opportunity_id}/restore", json={})
        assert restore.status_code == 200
        exclusion_id = exclusion.json()["id"]

    with TestClient(create_app(settings)) as client:
        detail = client.get("/api/opportunities").json()[0]
        assert detail["id"] == opportunity_id
        assert detail["tracking_status"] == "shortlisted"
        history = client.get(f"/api/opportunities/{opportunity_id}/assessments/personal/history").json()
        assert [item["revision_number"] for item in history] == [1, 2]
        assert client.get(f"/api/opportunities/{opportunity_id}/assessments/personal").json()[0]["value"] == 5
        decisions = client.get(f"/api/opportunities/{opportunity_id}/decisions").json()
        assert len(decisions) == 3
        assert decisions[-1]["reverses_decision_id"] == exclusion_id
