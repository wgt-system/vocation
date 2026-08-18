from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from vocation.api.app import create_app
from vocation.config import get_settings


def test_seeded_vocabularies_are_searchable_by_alias(client: TestClient) -> None:
    roles = client.get("/api/search-vocabularies", params={"kind": "role"})
    assert roles.status_code == 200
    assert any(entry["label"] == "AI Engineer" for entry in roles.json())

    technology = client.get(
        "/api/search-vocabularies",
        params={"kind": "technology", "q": "Golang"},
    )
    assert technology.status_code == 200
    assert [entry["label"] for entry in technology.json()] == ["Go"]


def test_custom_entry_is_durable_and_duplicate_normalization_is_rejected(tmp_path: Path) -> None:
    database_path = tmp_path / "vocation.db"
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{database_path.as_posix()}",
        frontend_dist=tmp_path / "no-frontend",
        application_document_store_dir=tmp_path / "application-documents",
    )

    with TestClient(create_app(settings)) as client:
        created = client.post(
            "/api/search-vocabularies/custom",
            json={
                "kind": "role",
                "label": "Creative AI Developer",
                "aliases": ["Creative AI Engineer"],
                "group": "AI & Data",
            },
        )
        assert created.status_code == 201
        entry_id = created.json()["id"]
        assert created.json()["is_custom"] is True

        duplicate = client.post(
            "/api/search-vocabularies/custom",
            json={"kind": "role", "label": "  creative   ai developer  "},
        )
        assert duplicate.status_code == 409

    with TestClient(create_app(settings)) as restarted:
        persisted = restarted.get(
            "/api/search-vocabularies",
            params={"kind": "role", "q": "Creative AI Engineer"},
        )
        assert persisted.status_code == 200
        assert [entry["id"] for entry in persisted.json()] == [entry_id]


def test_entry_can_be_deprecated_without_destructive_delete(client: TestClient) -> None:
    created = client.post(
        "/api/search-vocabularies/custom",
        json={"kind": "industry", "label": "Experimental Industry"},
    )
    assert created.status_code == 201
    entry_id = created.json()["id"]

    updated = client.patch(
        f"/api/search-vocabularies/{entry_id}",
        json={"is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    active = client.get(
        "/api/search-vocabularies",
        params={"kind": "industry", "q": "Experimental"},
    )
    assert active.json() == []

    including_inactive = client.get(
        "/api/search-vocabularies",
        params={
            "kind": "industry",
            "q": "Experimental",
            "include_inactive": True,
        },
    )
    assert [entry["id"] for entry in including_inactive.json()] == [entry_id]


def test_catalog_lifecycle_does_not_rewrite_search_profile_revision(client: TestClient) -> None:
    custom = client.post(
        "/api/search-vocabularies/custom",
        json={"kind": "role", "label": "Future Systems Engineer"},
    )
    assert custom.status_code == 201
    entry_id = custom.json()["id"]

    profile_payload = {
        "name": "Future role search",
        "description": "Test catalog stability",
        "target_roles": ["Future Systems Engineer"],
        "seniority_targets": ["Junior"],
        "preferred_technologies": ["Java"],
        "acceptable_technologies": [],
        "avoided_technologies": [],
        "target_locations": ["Hamburg"],
        "work_models": ["hybrid"],
        "relocation_willing": False,
        "employment_types": ["Vollzeit"],
        "preferred_industries": [],
        "avoided_industries": [],
        "preferred_company_characteristics": [],
        "avoided_company_characteristics": [],
        "salary_floor": None,
        "salary_target": None,
        "salary_currency": "EUR",
        "must_haves": [],
        "must_not_haves": [],
        "result_limit": 10,
        "criterion_policies": [],
    }
    profile = client.post("/api/profiles/search", json=profile_payload)
    assert profile.status_code == 201

    deprecated = client.patch(
        f"/api/search-vocabularies/{entry_id}",
        json={"label": "Future Platform Engineer", "is_active": False},
    )
    assert deprecated.status_code == 200

    stored = client.get(f"/api/profiles/search/{profile.json()['id']}")
    assert stored.status_code == 200
    assert stored.json()["target_roles"] == ["Future Systems Engineer"]
