from __future__ import annotations

from tests.test_imports import import_bundle, valid_bundle


def opportunity_id(client) -> str:
    return client.get("/api/opportunities").json()[0]["id"]


def test_personal_assessment_revision_is_immutable_and_separate_from_external(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    created = client.post(
        f"/api/opportunities/{oid}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "Good entry point"},
    )
    assert created.status_code == 201
    revised = client.post(
        f"/api/opportunities/{oid}/assessments/personal/{created.json()['id']}/revisions",
        json={"value": 5, "reasoning": "Reviewed details"},
    )
    assert revised.status_code == 201
    history = client.get(f"/api/opportunities/{oid}/assessments/personal/history").json()
    assert [item["revision_number"] for item in history] == [1, 2]
    assert history[1]["supersedes_id"] == history[0]["id"]
    detail = client.get(f"/api/opportunities/{oid}").json()
    assert len(detail["external_assessments"]) == 1
    assert detail["personal_assessments"][0]["value"] == 5


def test_decision_exclusion_restore_and_import_do_not_overwrite_personal_state(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    assert client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "Not suitable now"}).status_code == 200
    assert client.post(f"/api/opportunities/{oid}/restore", json={"target_status": "shortlisted"}).status_code == 200
    decisions = client.get(f"/api/opportunities/{oid}/decisions").json()
    assert [item["decision_type"] for item in decisions] == ["exclusion", "restore"]
    assert client.get("/api/opportunities").json()[0]["tracking_status"] == "shortlisted"
    assert import_bundle(client, valid_bundle()).status_code == 200
    assert client.get("/api/opportunities").json()[0]["tracking_status"] == "shortlisted"


def test_invalid_personal_value_and_empty_exclusion_are_rejected_atomically(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    assert (
        client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "junior_suitability", "value": 9}).status_code
        == 422
    )
    assert client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "   "}).status_code == 422
    assert client.get(f"/api/opportunities/{oid}/assessments/personal/history").json() == []
