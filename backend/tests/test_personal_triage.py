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


def test_repeated_import_preserves_personal_revisions_and_decision_history(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    first = client.post(
        f"/api/opportunities/{oid}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "first"},
    )
    assert first.status_code == 201
    second = client.post(
        f"/api/opportunities/{oid}/assessments/personal/{first.json()['id']}/revisions",
        json={"value": 5, "reasoning": "revised"},
    )
    assert second.status_code == 201
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "shortlisted"}).status_code == 200
    before_assessments = client.get(f"/api/opportunities/{oid}/assessments/personal/history").json()
    before_decisions = client.get(f"/api/opportunities/{oid}/decisions").json()
    assert import_bundle(client, valid_bundle()).status_code == 200
    assert client.get(f"/api/opportunities/{oid}/assessments/personal/history").json() == before_assessments
    assert client.get(f"/api/opportunities/{oid}/decisions").json() == before_decisions
    assert client.get(f"/api/opportunities/{oid}/assessments/personal").json()[0]["value"] == 5
    assert client.get(f"/api/opportunities/{oid}").json()["tracking_status"] == "shortlisted"
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


def test_create_duplicate_and_revision_conflicts_are_explicit(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    first = client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "junior_suitability", "value": 4})
    assert first.status_code == 201
    duplicate = client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "junior_suitability", "value": 5})
    assert duplicate.status_code == 409
    second = client.post(f"/api/opportunities/{oid}/assessments/personal/{first.json()['id']}/revisions", json={"value": 5})
    assert second.status_code == 201
    old_revision = client.post(f"/api/opportunities/{oid}/assessments/personal/{first.json()['id']}/revisions", json={"value": 3})
    assert old_revision.status_code == 409
    history = client.get(f"/api/opportunities/{oid}/assessments/personal/history").json()
    assert [item["revision_number"] for item in history] == [1, 2]
    assert history[0]["value"] == 4


def test_personal_assessment_validates_categorical_boolean_and_inactive_criteria(client) -> None:
    categorical = client.post(
        "/api/criteria",
        json={
            "criterion_id": "category_test",
            "display_name": "Category",
            "value_type": "categorical",
            "allowed_values": ["yes", "no"],
            "applicable_subject_type": "opportunity",
        },
    )
    assert categorical.status_code == 201
    boolean = client.post(
        "/api/criteria",
        json={"criterion_id": "boolean_test", "display_name": "Boolean", "value_type": "boolean", "applicable_subject_type": "opportunity"},
    )
    assert boolean.status_code == 201
    inactive = client.post(
        "/api/criteria",
        json={
            "criterion_id": "inactive_test",
            "display_name": "Inactive",
            "value_type": "text",
            "applicable_subject_type": "opportunity",
            "active": False,
        },
    )
    assert inactive.status_code == 201
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    assert (
        client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "category_test", "value": "yes"}).status_code
        == 201
    )
    assert (
        client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "category_test", "value": "other"}).status_code
        == 422
    )
    assert (
        client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "boolean_test", "value": True}).status_code
        == 201
    )
    assert (
        client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "inactive_test", "value": "kept"}).status_code
        == 422
    )


def test_personal_reference_protects_criterion_semantics_and_name_is_read(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    created = client.post(f"/api/opportunities/{oid}/assessments/personal", json={"criterion_id": "junior_suitability", "value": 4})
    assert created.status_code == 201
    criterion = next(item for item in client.get("/api/criteria").json() if item["criterion_id"] == "junior_suitability")
    criterion.pop("revision")
    criterion["numeric_max"] = 10
    assert client.put("/api/criteria/junior_suitability", json=criterion).status_code == 409
    criterion["numeric_max"] = 5
    criterion["display_name"] = "Junior fit"
    assert client.put("/api/criteria/junior_suitability", json=criterion).status_code == 200
    response = client.get(f"/api/opportunities/{oid}/assessments/personal")
    assert response.json()[0]["criterion_name"] == "Junior fit"
    assert client.post("/api/criteria/junior_suitability/activation", json={"active": False}).status_code == 200
    assert client.get(f"/api/opportunities/{oid}/assessments/personal/history").json()[0]["value"] == 4


def test_assessment_and_decision_queries_return_404_for_unknown_opportunity(client) -> None:
    for path in (
        "/api/opportunities/missing/assessments/personal",
        "/api/opportunities/missing/assessments/personal/history",
        "/api/opportunities/missing/decisions",
    ):
        assert client.get(path).status_code == 404


def test_status_exclusion_and_restore_invariants(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    assert client.get(f"/api/opportunities/{oid}").json()["tracking_status"] == "new"
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "shortlisted"}).status_code == 200
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "shortlisted"}).status_code == 409
    assert client.get(f"/api/opportunities/{oid}/decisions").json()[-1]["resulting_status"] == "shortlisted"
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "excluded"}).status_code == 422
    assert client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "  Not now  "}).status_code == 200
    assert client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "Again"}).status_code == 409
    restored = client.post(f"/api/opportunities/{oid}/restore", json={})
    assert restored.status_code == 200
    assert restored.json()["resulting_status"] == "shortlisted"
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "interesting"}).status_code == 200
    assert client.post(f"/api/opportunities/{oid}/status", json={"status": "new"}).status_code == 200
    assert client.post(f"/api/opportunities/{oid}/restore", json={}).status_code == 409


def test_restore_cycles_reverse_the_current_exclusion_only(client) -> None:
    assert import_bundle(client, valid_bundle()).status_code == 200
    oid = opportunity_id(client)
    client.post(f"/api/opportunities/{oid}/status", json={"status": "interesting"})
    first_exclusion = client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "E1"}).json()
    client.post(f"/api/opportunities/{oid}/restore", json={})
    client.post(f"/api/opportunities/{oid}/status", json={"status": "shortlisted"})
    second_exclusion = client.post(f"/api/opportunities/{oid}/exclude", json={"reason": "E2"}).json()
    second_restore = client.post(f"/api/opportunities/{oid}/restore", json={})
    assert second_restore.json()["reverses_decision_id"] == second_exclusion["id"]
    assert second_restore.json()["reverses_decision_id"] != first_exclusion["id"]
    assert [item["decision_type"] for item in client.get(f"/api/opportunities/{oid}/decisions").json()] == [
        "status_change",
        "exclusion",
        "restore",
        "status_change",
        "exclusion",
        "restore",
    ]
