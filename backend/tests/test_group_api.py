from __future__ import annotations

import json

from tests.test_imports import valid_bundle


def import_initial(client) -> str:
    response = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())})
    assert response.json()["status"] == "applied"
    return client.get("/api/opportunities").json()[0]["id"]


def test_group_crud_membership_and_reorder(client) -> None:
    opportunity_id = import_initial(client)
    created = client.post(
        "/api/groups",
        json={"name": "Priority Wave", "description": "First batch", "group_type": "application_wave"},
    )
    assert created.status_code == 201
    group_id = created.json()["id"]
    assert created.json()["memberships"] == []

    added = client.post(f"/api/groups/{group_id}/memberships", json={"opportunity_id": opportunity_id})
    assert added.status_code == 200
    assert added.json()["memberships"] == [
        {
            "opportunity_id": opportunity_id,
            "position": 0,
            "opportunity_title": "Junior Softwareentwickler",
            "company_name": "Example GmbH",
        }
    ]
    edited = client.put(f"/api/groups/{group_id}", json={"name": "Edited", "description": None, "group_type": "general"})
    assert edited.status_code == 200
    assert edited.json()["name"] == "Edited"
    assert client.get("/api/groups").json()[0]["id"] == group_id
    assert client.get(f"/api/groups/{group_id}").status_code == 200
    assert client.delete(f"/api/groups/{group_id}/memberships/{opportunity_id}").status_code == 200
    assert client.delete(f"/api/groups/{group_id}").status_code == 204
    assert client.get(f"/api/groups/{group_id}").status_code == 404


def test_group_reorder_and_opportunity_filter(client) -> None:
    opportunity_id = import_initial(client)
    second = client.post(
        "/api/groups",
        json={"name": "General", "description": None, "group_type": "general"},
    ).json()
    group_id = second["id"]
    assert client.post(f"/api/groups/{group_id}/memberships", json={"opportunity_id": opportunity_id}).status_code == 200
    assert client.put(f"/api/groups/{group_id}/order", json={"opportunity_ids": [opportunity_id]}).status_code == 200
    filtered = client.get(f"/api/opportunities?group_id={group_id}")
    assert filtered.status_code == 200
    assert [item["id"] for item in filtered.json()] == [opportunity_id]
    assert filtered.json()[0]["groups"] == [{"group_id": group_id, "name": "General", "group_type": "general"}]
    detail = client.get(f"/api/opportunities/{opportunity_id}")
    assert detail.status_code == 200
    assert detail.json()["groups"] == [{"group_id": group_id, "name": "General", "group_type": "general"}]
    assert client.get("/api/opportunities?group_id=missing").json() == []


def test_group_conflicts_and_not_found_are_mapped(client) -> None:
    opportunity_id = import_initial(client)
    assert client.get("/api/groups/missing").status_code == 404
    assert client.post("/api/groups", json={"name": " ", "description": None, "group_type": "general"}).status_code == 422
    group_id = client.post("/api/groups", json={"name": "Group", "description": None, "group_type": "general"}).json()["id"]
    assert client.post(f"/api/groups/{group_id}/memberships", json={"opportunity_id": "missing"}).status_code == 404
    assert client.post(f"/api/groups/{group_id}/memberships", json={"opportunity_id": opportunity_id}).status_code == 200
    assert client.post(f"/api/groups/{group_id}/memberships", json={"opportunity_id": opportunity_id}).status_code == 409
    assert client.put(f"/api/groups/{group_id}/order", json={"opportunity_ids": []}).status_code == 409
