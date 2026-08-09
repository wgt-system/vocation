from __future__ import annotations

import json
from pathlib import Path

from vocation.infrastructure.models import (
    CompanyModel,
    OpportunityModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptRunModel,
)


def _initial_bundle() -> str:
    return (Path(__file__).resolve().parents[2] / "examples" / "imports" / "initial-valid.json").read_text(
        encoding="utf-8"
    )


def _context(prompt_text: str) -> dict:
    body = prompt_text.split("## Prompt Context\n", 1)[1].split("\n\n## Active Assessment Criteria", 1)[0]
    return json.loads(body)


def _market_ids(app) -> tuple[str, str, str]:
    with app.state.database.session_factory() as session:
        company = session.query(CompanyModel).one()
        opportunity = session.query(OpportunityModel).one()
        posting = session.query(PostingModel).one()
        return company.id, opportunity.id, posting.id


def test_update_prompt_full_scope_is_public_and_persisted(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    company_id, opportunity_id, posting_id = _market_ids(app)

    result = app.state.prompt_service.generate_update(mode="full_update", as_of_date="2026-08-09")
    context = _context(result.prompt_text)

    assert result.bundle_version == "2.0"
    assert result.prompt_version == "1.0"
    assert context["research_scope"] == {"type": "full_update", "as_of_date": "2026-08-09"}
    assert len(context["known_subjects"]["companies"]) == 1
    assert len(context["known_subjects"]["opportunities"]) == 1
    assert len(context["known_subjects"]["postings"]) == 1
    assert all(item["is_target"] for group in context["known_subjects"].values() for item in group)
    assert company_id not in result.prompt_text
    assert opportunity_id not in result.prompt_text
    assert posting_id not in result.prompt_text
    assert "Tracking Status" not in json.dumps(context)
    assert "## Update Bundle 2.0" not in result.prompt_text
    assert '"bundle_version"' in result.prompt_text
    assert "bundle_version" in result.prompt_text
    assert "{{" not in result.prompt_text

    with app.state.database.session_factory() as session:
        run = session.get(PromptRunModel, result.prompt_run_id)
        snapshot = session.get(PromptContextSnapshotModel, result.prompt_context_ref)
        assert run is not None
        assert snapshot is not None
        assert run.prompt_type == "full_update"
        assert run.bundle_version == "2.0"
        assert run.prompt_version == "1.0"
        assert run.prompt_context_ref == result.prompt_context_ref
        assert snapshot.scope_type == "full_update"


def test_update_prompt_scopes_and_gap_requests_use_correlation_refs(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    company_id, opportunity_id, posting_id = _market_ids(app)

    company_result = app.state.prompt_service.generate_update(
        mode="company_update", as_of_date="2026-08-09", selected_ids=[company_id]
    )
    company_context = _context(company_result.prompt_text)
    assert company_context["research_scope"]["selected_correlation_refs"] == [
        company_context["known_subjects"]["companies"][0]["correlation_ref"]
    ]
    assert all(item["is_target"] for group in company_context["known_subjects"].values() for item in group)

    opportunity_result = app.state.prompt_service.generate_update(
        mode="opportunity_update", as_of_date="2026-08-09", selected_ids=[opportunity_id]
    )
    opportunity_context = _context(opportunity_result.prompt_text)
    assert opportunity_context["known_subjects"]["companies"][0]["is_target"] is False
    assert opportunity_context["known_subjects"]["opportunities"][0]["is_target"] is True
    assert opportunity_context["known_subjects"]["postings"][0]["is_target"] is True

    gap_result = app.state.prompt_service.generate_update(
        mode="gap_filling",
        as_of_date="2026-08-09",
        gap_requests=[
            {"subject_type": "posting", "subject_id": posting_id, "observation_type": "technology_requirement"},
            {"subject_type": "opportunity", "subject_id": opportunity_id, "criterion_id": "junior_suitability"},
        ],
    )
    gap_context = _context(gap_result.prompt_text)
    requests = gap_context["research_scope"]["requests"]
    assert [request["subject_type"] for request in requests] == ["posting", "opportunity"]
    assert all("internal_id" not in json.dumps(request) for request in requests)
    assert len(gap_context["known_subjects"]["postings"]) == 1
    assert len(gap_context["known_subjects"]["opportunities"]) == 1
    assert len(gap_context["known_subjects"]["companies"]) == 1
    assert gap_context["known_subjects"]["companies"][0]["is_target"] is False
    assert all(
        item["is_target"]
        for name, group in gap_context["known_subjects"].items()
        if name != "companies"
        for item in group
    )
    assert {item["type"] for item in gap_context["latest_observations"]} == {"technology_requirement"}
    assert {item["criterion_id"] for item in gap_context["latest_external_assessments"]} == {"junior_suitability"}
    assert gap_context["unresolved_duplicate_cases"] == []
