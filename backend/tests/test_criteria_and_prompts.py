from __future__ import annotations

from datetime import date


def _search_profile_payload() -> dict:
    return {
        "name": "Junior Python Hamburg",
        "description": "Quality-first entry-level search.",
        "target_roles": ["Junior Softwareentwickler"],
        "seniority_targets": ["junior"],
        "preferred_technologies": ["Python"],
        "acceptable_technologies": ["Java"],
        "avoided_technologies": [],
        "target_locations": ["Hamburg"],
        "work_models": ["hybrid"],
        "relocation_willing": False,
        "employment_types": ["full-time"],
        "preferred_industries": ["Software"],
        "avoided_industries": [],
        "preferred_company_characteristics": ["gute Einarbeitung"],
        "avoided_company_characteristics": [],
        "salary_floor": None,
        "salary_target": None,
        "salary_currency": "EUR",
        "must_haves": ["Berufseinstieg möglich"],
        "must_not_haves": ["Senior-only"],
        "result_limit": 7,
        "criterion_policies": [],
    }


def test_seeded_criteria_can_be_listed_and_managed(client) -> None:
    response = client.get("/api/criteria")
    assert response.status_code == 200
    criteria = response.json()
    assert [item["criterion_id"] for item in criteria] == [
        "junior_suitability",
        "technology_fit",
        "role_clarity",
        "work_model_fit",
    ]

    created = client.post(
        "/api/criteria",
        json={
            "criterion_id": "documentation_quality",
            "display_name": "Dokumentationsqualität",
            "description": "Qualität der verfügbaren Rollendetails",
            "value_type": "categorical",
            "allowed_values": ["good", "limited", "unknown"],
            "applicable_subject_type": "opportunity",
            "active": True,
            "display_order": 50,
        },
    )
    assert created.status_code == 201
    assert created.json()["revision"] == 1

    deactivated = client.post(
        "/api/criteria/documentation_quality/activation",
        json={"active": False},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["active"] is False

    ids = [item["criterion_id"] for item in client.get("/api/criteria").json()]
    reordered = client.post("/api/criteria/reorder", json={"criterion_ids": list(reversed(ids))})
    assert reordered.status_code == 200
    assert [item["criterion_id"] for item in reordered.json()] == list(reversed(ids))

    editable = next(item for item in reordered.json() if item["criterion_id"] == "junior_suitability")
    editable["display_name"] = "Junior-Passung"
    editable.pop("revision")
    edited = client.put("/api/criteria/junior_suitability", json=editable)
    assert edited.status_code == 200
    assert edited.json()["display_name"] == "Junior-Passung"


def test_generated_prompt_is_profile_aware_quality_first_and_self_contained(client) -> None:
    client.post("/api/criteria/work_model_fit/activation", json={"active": False})
    profile = client.post("/api/profiles/search", json=_search_profile_payload())
    assert profile.status_code == 201
    candidate = client.put(
        "/api/profiles/candidate",
        json={
            "headline": "Junior Softwareentwickler",
            "summary": "Informatikprofil mit Python- und Java-Erfahrung.",
        },
    )
    assert candidate.status_code == 200

    response = client.post(
        "/api/prompts/initial",
        json={
            "search_profile": profile.json()["id"],
            "constraints": [],
            "as_of_date": date(2026, 8, 6).isoformat(),
        },
    )
    assert response.status_code == 200
    generated = response.json()
    prompt = generated["prompt_text"]
    assert generated["criteria_count"] == 3
    assert "junior_suitability" in prompt
    assert "technology_fit" in prompt
    assert "role_clarity" in prompt
    assert "work_model_fit" not in prompt
    assert "source_references: SourceReference[]" in prompt
    assert '"type": "initial_market_research"' in prompt
    assert '"name": "Junior Python Hamburg"' in prompt
    assert '"result_limit": 7' in prompt
    assert "Must have: Berufseinstieg möglich" in prompt
    assert "Must not have: Senior-only" in prompt
    assert "Junior Softwareentwickler" in prompt
    assert "upper bound, not a target" in prompt
    assert "Prefer fewer concrete opportunities" in prompt
    assert "2026-08-06" in prompt
    assert "schemas/research-bundle" not in prompt
    assert "{{" not in prompt


def test_referenced_criterion_requires_new_id_for_incompatible_change(client) -> None:
    from pathlib import Path

    bundle = (Path(__file__).resolve().parents[2] / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8")
    assert client.post("/api/imports/text", json={"content": bundle}).json()["status"] == "applied"
    criterion = next(item for item in client.get("/api/criteria").json() if item["criterion_id"] == "junior_suitability")
    criterion.pop("revision")
    criterion["numeric_max"] = 10
    response = client.put("/api/criteria/junior_suitability", json=criterion)
    assert response.status_code == 409
    assert "create a new ID" in response.json()["detail"]