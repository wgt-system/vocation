from __future__ import annotations

import json

from tests.test_imports import valid_bundle


def import_initial(client) -> str:
    response = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    return client.get("/api/opportunities").json()[0]["id"]


def test_create_list_and_get_application_case(client) -> None:
    opportunity_id = import_initial(client)

    created = client.post(f"/api/opportunities/{opportunity_id}/application-cases")
    assert created.status_code == 201
    case = created.json()
    assert case["lifecycle"] == "draft"
    assert case["opportunity_id"] == opportunity_id
    assert case["lifecycle_events"] == [
        {
            "previous_status": None,
            "resulting_status": "draft",
            "occurred_at": case["created_at"],
        }
    ]

    case_id = case["id"]
    assert client.get(f"/api/opportunities/{opportunity_id}/application-cases").json() == [case]
    assert client.get(f"/api/application-cases/{case_id}").json() == case


def test_active_case_and_lifecycle_conflicts_are_mapped(client) -> None:
    opportunity_id = import_initial(client)
    first = client.post(f"/api/opportunities/{opportunity_id}/application-cases").json()

    assert client.post(f"/api/opportunities/{opportunity_id}/application-cases").status_code == 409
    assert client.post(f"/api/application-cases/{first['id']}/lifecycle", json={"lifecycle": "draft"}).status_code == 409
    assert client.post(f"/api/application-cases/{first['id']}/lifecycle", json={"lifecycle": "accepted"}).status_code == 200
    assert client.post(f"/api/application-cases/{first['id']}/lifecycle", json={"lifecycle": "ready"}).status_code == 409
    assert client.post(f"/api/application-cases/{first['id']}/lifecycle", json={"lifecycle": "not-a-lifecycle"}).status_code == 422


def test_lifecycle_endpoint_appends_history_and_materials_are_revised(client) -> None:
    opportunity_id = import_initial(client)
    case = client.post(f"/api/opportunities/{opportunity_id}/application-cases").json()

    changed = client.post(f"/api/application-cases/{case['id']}/lifecycle", json={"lifecycle": "ready"})
    assert changed.status_code == 200
    assert [event["resulting_status"] for event in changed.json()["lifecycle_events"]] == ["draft", "ready"]

    material_response = client.post(
        f"/api/application-cases/{case['id']}/materials",
        json={"kind": "cv", "display_name": "  Resume  "},
    )
    assert material_response.status_code == 201
    material = material_response.json()
    assert material["revision"] == 1
    assert material["display_name"] == "Resume"

    revised = client.post(f"/api/application-materials/{material['id']}/revisions", json={"display_name": "  Resume final  "})
    assert revised.status_code == 201
    assert revised.json()["revision"] == 2
    assert revised.json()["display_name"] == "Resume final"
    assert client.get(f"/api/application-cases/{case['id']}/materials").json() == [revised.json()]


def test_missing_resources_and_invalid_material_input_are_mapped(client) -> None:
    opportunity_id = import_initial(client)

    assert client.get("/api/opportunities/missing/application-cases").status_code == 404
    assert client.post("/api/opportunities/missing/application-cases").status_code == 404
    assert client.get("/api/application-cases/missing").status_code == 404
    assert client.get("/api/application-cases/missing/materials").status_code == 404
    assert client.post("/api/application-materials/missing/revisions", json={"display_name": "Resume"}).status_code == 404

    case = client.post(f"/api/opportunities/{opportunity_id}/application-cases").json()
    assert (
        client.post(f"/api/application-cases/{case['id']}/materials", json={"kind": "invalid", "display_name": "Resume"}).status_code == 422
    )
    assert client.post(f"/api/application-cases/{case['id']}/materials", json={"kind": "cv", "display_name": " "}).status_code == 422
    assert (
        client.post(
            f"/api/application-cases/{case['id']}/materials",
            json={"kind": "cv", "display_name": "Resume", "unexpected": True},
        ).status_code
        == 422
    )


def test_application_cases_do_not_change_tracking_status(client) -> None:
    opportunity_id = import_initial(client)
    before = client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"]
    case = client.post(f"/api/opportunities/{opportunity_id}/application-cases").json()
    client.post(f"/api/application-cases/{case['id']}/lifecycle", json={"lifecycle": "ready"})
    material = client.post(f"/api/application-cases/{case['id']}/materials", json={"kind": "other", "display_name": "Notes"}).json()
    client.post(f"/api/application-materials/{material['id']}/revisions", json={"display_name": "Notes final"})

    assert client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"] == before


def test_application_routes_are_internal_openapi_only(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    expected = {
        "/api/opportunities/{opportunity_id}/application-cases",
        "/api/application-cases/{case_id}",
        "/api/application-cases/{case_id}/lifecycle",
        "/api/application-cases/{case_id}/materials",
        "/api/application-materials/{material_id}/revisions",
    }
    assert expected <= set(paths)
    assert not any(path.startswith("/published/") and "application" in path for path in paths)
