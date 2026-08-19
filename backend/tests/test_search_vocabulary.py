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


def test_refresh_prompt_is_self_contained_and_excludes_places(client: TestClient) -> None:
    generated = client.post(
        "/api/search-vocabularies/refresh-prompt",
        json={
            "as_of_date": "2026-08-18",
            "kinds": ["role", "technology", "industry"],
        },
    )
    assert generated.status_code == 200
    payload = generated.json()
    assert payload["prompt_version"] == "1.0"
    assert payload["as_of_date"] == "2026-08-18"
    assert "AI Engineer" in payload["prompt_text"]
    assert "PostgreSQL" in payload["prompt_text"]
    assert '"contract": "vocation.search-vocabulary-proposals"' in payload["prompt_text"]
    assert "Do not research geographic places" in payload["prompt_text"]


def test_proposal_review_marks_known_terms_without_mutating_catalog(client: TestClient) -> None:
    before = client.get("/api/search-vocabularies", params={"kind": "role"}).json()
    bundle = {
        "contract": "vocation.search-vocabulary-proposals",
        "version": "1.0",
        "as_of_date": "2026-08-18",
        "proposals": [
            {
                "kind": "role",
                "label": "AI Engineer",
                "aliases": ["Artificial Intelligence Engineer"],
                "group": "AI & Data",
                "reason": "Already represented in the current market catalog.",
                "source_urls": ["https://example.com/ai-engineer"],
            },
            {
                "kind": "role",
                "label": "Agentic Systems Engineer",
                "aliases": ["Agentic AI Engineer"],
                "group": "AI & Data",
                "reason": "A hypothetical new market term for explicit review.",
                "source_urls": ["https://example.com/agentic-systems"],
            },
        ],
    }

    reviewed = client.post("/api/search-vocabularies/proposals/review", json=bundle)
    assert reviewed.status_code == 200
    proposals = reviewed.json()["proposals"]
    assert proposals[0]["already_known_entry_id"] == "role-ai-engineer"
    assert proposals[1]["already_known_entry_id"] is None

    after = client.get("/api/search-vocabularies", params={"kind": "role"}).json()
    assert after == before

    accepted = client.post(
        "/api/search-vocabularies/custom",
        json={
            "kind": proposals[1]["proposal"]["kind"],
            "label": proposals[1]["proposal"]["label"],
            "aliases": proposals[1]["proposal"]["aliases"],
            "group": proposals[1]["proposal"]["group"],
        },
    )
    assert accepted.status_code == 201
    assert accepted.json()["label"] == "Agentic Systems Engineer"


def test_proposal_review_requires_https_evidence(client: TestClient) -> None:
    invalid = client.post(
        "/api/search-vocabularies/proposals/review",
        json={
            "contract": "vocation.search-vocabulary-proposals",
            "version": "1.0",
            "as_of_date": "2026-08-18",
            "proposals": [
                {
                    "kind": "technology",
                    "label": "FutureDB",
                    "aliases": [],
                    "group": "Datenbank",
                    "reason": "Needs evidence.",
                    "source_urls": ["http://example.com/futuredb"],
                }
            ],
        },
    )
    assert invalid.status_code == 422
