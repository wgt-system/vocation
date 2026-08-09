from __future__ import annotations

import json
from pathlib import Path

from tests.test_imports import valid_bundle
from vocation.infrastructure.models import CompanyModel, OpportunityModel, PostingModel

ROOT = Path(__file__).resolve().parents[2]


def _ids(app) -> tuple[str, str, str]:
    with app.state.database.session_factory() as session:
        company = session.query(CompanyModel).one()
        opportunity = session.query(OpportunityModel).one()
        posting = session.query(PostingModel).one()
        return company.id, opportunity.id, posting.id


def _prompt_context(prompt_text: str) -> dict:
    return json.loads(prompt_text.split("## Prompt Context\n", 1)[1].split("\n\n## Active Assessment Criteria", 1)[0])


def test_update_options_exposes_only_external_market_graph(client) -> None:
    assert client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()["status"] == "applied"
    response = client.get("/api/prompts/update-options")
    assert response.status_code == 200
    assert set(response.json()) == {"companies", "opportunities", "postings", "observation_types"}
    assert len(response.json()["companies"]) == 1
    assert response.json()["companies"][0]["name"] == "Example GmbH"
    assert set(response.json()["opportunities"][0]) == {"id", "company_id", "title"}
    assert set(response.json()["postings"][0]) == {"id", "company_id", "opportunity_id", "title"}
    assert response.json()["observation_types"] == [
        "technology_requirement",
        "task",
        "seniority",
        "experience_requirement",
        "work_model",
        "salary",
    ]
    assert "tracking_status" not in json.dumps(response.json())
    assert "personal" not in json.dumps(response.json()).lower()


def test_all_update_modes_are_available_through_http(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()["status"] == "applied"
    company_id, opportunity_id, posting_id = _ids(app)
    payloads = [
        {"mode": "full_update", "as_of_date": "2026-08-09"},
        {"mode": "company_update", "as_of_date": "2026-08-09", "selected_ids": [company_id]},
        {"mode": "opportunity_update", "as_of_date": "2026-08-09", "selected_ids": [opportunity_id]},
        {
            "mode": "gap_filling",
            "as_of_date": "2026-08-09",
            "gap_requests": [{"subject_type": "posting", "subject_id": posting_id, "observation_type": "task"}],
        },
    ]
    for payload in payloads:
        response = client.post("/api/prompts/update", json=payload)
        assert response.status_code == 200, response.text
        assert set(response.json()) == {
            "prompt_run_id",
            "prompt_context_ref",
            "prompt_type",
            "prompt_version",
            "bundle_version",
            "research_scope",
            "prompt_text",
            "criteria_count",
        }
        assert response.json()["bundle_version"] == "2.0"


def test_update_prompt_structural_shapes_are_rejected(client) -> None:
    invalid_payloads = [
        {"mode": "unknown", "as_of_date": "2026-08-09"},
        {"mode": "full_update", "as_of_date": "2026-08-09", "selected_ids": ["x"]},
        {"mode": "company_update", "as_of_date": "2026-08-09"},
        {"mode": "company_update", "as_of_date": "2026-08-09", "selected_ids": ["x", "x"]},
        {"mode": "opportunity_update", "as_of_date": "2026-08-09", "selected_ids": ["x"], "gap_requests": [{}]},
        {"mode": "gap_filling", "as_of_date": "2026-08-09"},
        {
            "mode": "gap_filling",
            "as_of_date": "2026-08-09",
            "gap_requests": [{"subject_type": "posting", "subject_id": "x", "observation_type": "task", "criterion_id": "x"}],
        },
    ]
    for payload in invalid_payloads:
        assert client.post("/api/prompts/update", json=payload).status_code == 422


def test_generated_full_prompt_context_can_drive_update_import_and_traceability(client) -> None:
    initial = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()
    assert initial["bundle_version"] == "1.0"
    assert initial["prompt_context_ref"] is None
    generated = client.post("/api/prompts/update", json={"mode": "full_update", "as_of_date": "2026-08-09"}).json()
    context = _prompt_context(generated["prompt_text"])
    bundle = json.loads((ROOT / "examples" / "updates" / "full-update-valid.json").read_text(encoding="utf-8"))
    bundle["prompt_context_ref"] = generated["prompt_context_ref"]
    bundle["research_scope"] = context["research_scope"]
    applied = client.post("/api/imports/text", json={"content": json.dumps(bundle)}).json()
    assert applied["status"] == "applied", applied["issues"]
    assert applied["bundle_version"] == "2.0"
    assert applied["prompt_context_ref"] == generated["prompt_context_ref"]
    report = client.get(f"/api/imports/{applied['import_id']}").json()
    assert report["bundle_version"] == "2.0"
    assert report["prompt_context_ref"] == generated["prompt_context_ref"]
    duplicate = client.post("/api/imports/text", json={"content": json.dumps(bundle)}).json()
    assert duplicate["status"] == "duplicate"
    assert duplicate["duplicate_of_import_id"] == applied["import_id"]
    assert duplicate["bundle_version"] == "2.0"
    assert duplicate["prompt_context_ref"] == generated["prompt_context_ref"]


def test_initial_prompt_endpoint_remains_unchanged(client) -> None:
    response = client.post(
        "/api/prompts/initial",
        json={"search_profile": "Python roles", "constraints": [], "as_of_date": "2026-08-09"},
    )
    assert response.status_code == 200
    assert set(response.json()) == {"prompt_run_id", "prompt_text", "bundle_version", "criteria_count"}
    assert response.json()["bundle_version"] == "1.0"
