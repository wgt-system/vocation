from __future__ import annotations


def candidate_payload(*, headline: str = "Softwareentwickler") -> dict:
    return {
        "headline": headline,
        "summary": "Informatikprofil mit Softwareentwicklungsfokus.",
        "education": [
            {
                "degree": "B.Sc.",
                "field": "Informatik",
                "institution": "Beispieluniversität",
                "status": "completed",
                "graduation_year": 2026,
            }
        ],
        "skills": [
            {"name": "Java", "level": "strong", "notes": "Backend und Build-Tooling"},
            {"name": "C++", "level": "working", "notes": None},
        ],
        "languages": [{"name": "Deutsch", "level": "native"}],
        "experience_summary": "Studium und eigene Softwareprojekte.",
        "projects": [
            {
                "name": "Beispielprojekt",
                "summary": "Lokale Desktop-Anwendung",
                "technologies": ["C++", "Qt"],
            }
        ],
        "interests": ["Softwarearchitektur", "Open Source"],
    }


def search_payload(*, name: str = "Junior Hamburg", preferred: list[str] | None = None) -> dict:
    return {
        "name": name,
        "description": "Qualitative Suche nach passenden Einstiegsstellen.",
        "target_roles": ["Junior Softwareentwickler", "Software Engineer"],
        "seniority_targets": ["junior", "entry level"],
        "preferred_technologies": preferred or ["Java", "C++"],
        "acceptable_technologies": ["Python"],
        "avoided_technologies": ["SAP ABAP"],
        "target_locations": ["Hamburg"],
        "work_models": ["hybrid", "remote"],
        "relocation_willing": True,
        "employment_types": ["full-time"],
        "preferred_industries": ["Software"],
        "avoided_industries": [],
        "preferred_company_characteristics": ["gute Einarbeitung"],
        "avoided_company_characteristics": ["reine Arbeitnehmerüberlassung"],
        "salary_floor": 40000,
        "salary_target": 50000,
        "salary_currency": "EUR",
        "must_haves": ["für Berufseinstieg geeignet"],
        "must_not_haves": ["mehrjährige Berufserfahrung zwingend"],
        "result_limit": 10,
    }


def test_candidate_profile_is_private_revisioned_local_state(client) -> None:
    assert client.get("/api/profiles/candidate").json() is None

    first = client.put("/api/profiles/candidate", json=candidate_payload())
    assert first.status_code == 200
    assert first.json()["revision"] == 1
    assert first.json()["skills"][0]["name"] == "Java"

    second = client.put("/api/profiles/candidate", json=candidate_payload(headline="Junior Softwareentwickler"))
    assert second.status_code == 200
    assert second.json()["revision"] == 2
    assert client.get("/api/profiles/candidate").json()["headline"] == "Junior Softwareentwickler"

    assert "/api/profiles/candidate" in client.app.openapi()["paths"]
    assert "/published/v1/opportunity-overview" not in client.app.openapi()["paths"]


def test_search_profiles_support_multiple_profiles_revisions_and_one_default(client) -> None:
    first = client.post("/api/profiles/search", json=search_payload())
    second = client.post("/api/profiles/search", json=search_payload(name="Berlin Java", preferred=["Java"]))
    assert first.status_code == 201
    assert second.status_code == 201
    assert len(client.get("/api/profiles/search").json()) == 2

    first_id = first.json()["id"]
    second_id = second.json()["id"]
    selected = client.post(f"/api/profiles/search/{first_id}/default")
    assert selected.status_code == 200
    assert selected.json()["is_default"] is True
    assert client.get("/api/profiles/search/default").json()["id"] == first_id

    selected = client.post(f"/api/profiles/search/{second_id}/default")
    assert selected.status_code == 200
    profiles = {item["id"]: item for item in client.get("/api/profiles/search").json()}
    assert profiles[first_id]["is_default"] is False
    assert profiles[second_id]["is_default"] is True

    revised_payload = search_payload(name="Junior Hamburg")
    revised_payload["result_limit"] = 7
    revised = client.put(f"/api/profiles/search/{first_id}", json=revised_payload)
    assert revised.status_code == 200
    assert revised.json()["revision"] == 2
    assert revised.json()["result_limit"] == 7


def test_search_profile_validation_rejects_ambiguous_technology_tiers(client) -> None:
    payload = search_payload()
    payload["acceptable_technologies"] = ["Java"]
    response = client.post("/api/profiles/search", json=payload)
    assert response.status_code == 422
    assert "only one preference tier" in response.json()["detail"]


def test_search_profile_name_conflict_and_delete_are_explicit(client) -> None:
    first = client.post("/api/profiles/search", json=search_payload())
    assert first.status_code == 201
    assert client.post("/api/profiles/search", json=search_payload()).status_code == 409

    profile_id = first.json()["id"]
    assert client.delete(f"/api/profiles/search/{profile_id}").status_code == 204
    assert client.get(f"/api/profiles/search/{profile_id}").status_code == 404
