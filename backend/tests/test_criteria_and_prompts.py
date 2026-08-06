from __future__ import annotations

from datetime import date


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


def test_generated_prompt_is_self_contained_and_contains_active_criteria(client) -> None:
    client.post("/api/criteria/work_model_fit/activation", json={"active": False})
    response = client.post(
        "/api/prompts/initial",
        json={
            "search_profile": "Junior Python roles",
            "constraints": ["Hamburg", "Hybrid possible"],
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
    assert 'type: "initial_market_research"' in prompt
    assert "Junior Python roles" in prompt
    assert "2026-08-06" in prompt
    assert "schemas/research-bundle" not in prompt
    assert "{{" not in prompt
