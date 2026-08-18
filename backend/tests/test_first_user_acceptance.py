from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from tests.test_profiles import search_payload
from vocation.api.app import create_app
from vocation.config import get_settings
from vocation.infrastructure.models import PromptRunModel
from vocation.infrastructure.prompt_context_repository import SqlAlchemyPromptContextSnapshotRepository

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "examples" / "acceptance" / "first-user-market.json"


def load_market_bundle() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def prompt_context_from_text(prompt_text: str) -> dict:
    return json.loads(
        prompt_text.split("## Prompt Context\n", 1)[1]
        .split("\n\n## Active Assessment Criteria", 1)[0]
    )


def initial_prompt_context(client: TestClient, prompt_run_id: str):
    database = client.app.state.database
    with database.session_factory() as session:
        run = session.get(PromptRunModel, prompt_run_id)
        assert run is not None
        assert run.prompt_context_ref is not None
        context_ref = run.prompt_context_ref
    context = SqlAlchemyPromptContextSnapshotRepository(
        database.session_factory
    ).get(context_ref)
    assert context is not None
    return context


def opportunity_ids_by_title(client: TestClient) -> dict[str, str]:
    return {item["title"]: item["id"] for item in client.get("/api/opportunities").json()}


def update_bundle(generated: dict) -> dict:
    context = prompt_context_from_text(generated["prompt_text"])
    company = context["known_subjects"]["companies"][0]
    opportunity = context["known_subjects"]["opportunities"][0]
    posting = context["known_subjects"]["postings"][0]
    return {
        "bundle_version": "2.0",
        "bundle_id": "acceptance-opportunity-update-001",
        "generated_at": "2026-08-19T10:00:00Z",
        "prompt_context_ref": generated["prompt_context_ref"],
        "research_scope": generated["research_scope"],
        "sources": [
            {
                "id": "src-acceptance-update",
                "name": "Example Careers",
                "type": "company_careers",
                "base_url": "https://example.com/careers",
            }
        ],
        "source_references": [
            {
                "id": "ref-acceptance-update",
                "source_id": "src-acceptance-update",
                "url": "https://example.com/jobs/junior-softwareentwickler?checked=2026-08-19",
                "observed_at": "2026-08-19T09:30:00Z",
            }
        ],
        "companies": [
            {
                "id": "company-context",
                "correlation_ref": company["correlation_ref"],
            }
        ],
        "opportunities": [
            {
                "id": "opportunity-context",
                "company_id": "company-context",
                "correlation_ref": opportunity["correlation_ref"],
            }
        ],
        "postings": [
            {
                "id": "posting-context",
                "company_id": "company-context",
                "opportunity_id": "opportunity-context",
                "correlation_ref": posting["correlation_ref"],
                "identity_evidence": {
                    "source_reference_id": "ref-acceptance-update",
                    "external_posting_id": posting["external_posting_id"],
                },
            }
        ],
        "observations": [
            {
                "id": "obs-acceptance-work-model",
                "subject_type": "opportunity",
                "subject_id": "opportunity-context",
                "type": "work_model",
                "value": "hybrid",
                "source_reference_id": "ref-acceptance-update",
                "observed_at": "2026-08-19T09:30:00Z",
                "evidence_summary": "Official posting still states hybrid work.",
            }
        ],
        "assessments": [],
        "possible_duplicates": [],
        "warnings": [],
    }


def test_first_user_profile_research_analysis_personal_state_update_and_restart(tmp_path: Path) -> None:
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{(tmp_path / 'first-user.db').as_posix()}",
        frontend_dist=tmp_path / "no-frontend",
    )
    profile_id: str
    target_id: str
    group_id: str
    initial_source_url = "https://example.com/jobs/junior-softwareentwickler"

    with TestClient(create_app(settings)) as client:
        candidate = client.put(
            "/api/profiles/candidate",
            json={
                "headline": "Junior Softwareentwickler",
                "summary": "B.Sc. Informatik mit Java- und Maven-Erfahrung.",
                "skills": [
                    {"name": "Java", "level": "strong", "notes": "Maven projects"},
                    {
                        "name": "PostgreSQL",
                        "level": "working",
                        "notes": "Project experience",
                    },
                ],
            },
        )
        assert candidate.status_code == 200
        assert candidate.json()["revision"] == 1

        profile_payload = search_payload(name="Hamburg Junior Software")
        profile_payload["must_haves"] = []
        profile_payload["must_not_haves"] = []
        profile_payload["result_limit"] = 5
        profile_payload["criterion_policies"] = [
            {
                "criterion_id": "junior_suitability",
                "weight": 3.0,
                "required": True,
                "minimum_numeric_value": 3,
            }
        ]
        profile = client.post("/api/profiles/search", json=profile_payload)
        assert profile.status_code == 201, profile.text
        profile_id = profile.json()["id"]
        assert client.post(f"/api/profiles/search/{profile_id}/default").status_code == 200

        initial_prompt = client.post(
            "/api/prompts/initial?include_candidate_profile=true",
            json={
                "search_profile": profile_id,
                "constraints": [],
                "as_of_date": "2026-08-18",
            },
        )
        assert initial_prompt.status_code == 200, initial_prompt.text
        generated = initial_prompt.json()
        context = initial_prompt_context(client, generated["prompt_run_id"])
        assert initial_prompt.headers["X-Prompt-Context-Ref"] == context.prompt_context_ref
        assert context.scope_json["search_profile"]["id"] == profile_id
        assert context.scope_json["search_profile"]["revision"] == 1
        assert context.scope_json["candidate_profile"]["revision"] == 1
        assert context.scope_json["research_scope"] == load_market_bundle()["research_scope"]
        assert "Hamburg Junior Software" in generated["prompt_text"]
        assert "Junior Softwareentwickler" in generated["prompt_text"]

        initial_import = client.post(
            f"/api/imports/text?prompt_run_id={generated['prompt_run_id']}",
            json={"content": json.dumps(load_market_bundle(), ensure_ascii=False)},
        )
        assert initial_import.status_code == 200
        assert initial_import.json()["status"] == "applied", initial_import.json()["issues"]
        assert (
            initial_import.json()["prompt_context_ref"]
            == context.prompt_context_ref
        )

        opportunities = client.get("/api/opportunities").json()
        assert len(opportunities) == 3
        ids = opportunity_ids_by_title(client)
        target_id = ids["Junior Softwareentwickler"]
        fit_results = {
            title: client.get(
                f"/api/opportunities/{opportunity_id}/fit?search_profile_id={profile_id}"
            ).json()
            for title, opportunity_id in ids.items()
        }
        assert (
            fit_results["Junior Softwareentwickler"]["hard_constraint_status"]
            == "pass"
        )
        assert (
            fit_results["Junior Backend Engineer"]["hard_constraint_status"]
            == "pass"
        )
        assert fit_results["Platform Developer"]["hard_constraint_status"] == "fail"
        assert (
            fit_results["Junior Softwareentwickler"]["weighted_fit_score"]
            > fit_results["Platform Developer"]["weighted_fit_score"]
        )

        detail_before = client.get(f"/api/opportunities/{target_id}").json()
        assert (
            detail_before["postings"][0]["source_reference"]["url"]
            == initial_source_url
        )
        assert (
            detail_before["external_assessments"][0]["origin"]
            == "external_research"
        )

        note = client.put(
            f"/api/opportunities/{target_id}/note",
            json={"content": "Gute Java-/Maven-Passung; Teamgröße im Gespräch klären."},
        )
        assert note.status_code == 200
        status = client.post(
            f"/api/opportunities/{target_id}/status",
            json={"status": "shortlisted"},
        )
        assert status.status_code == 200
        group = client.post(
            "/api/groups",
            json={
                "name": "Erste Bewerbungswelle",
                "description": "Stärkste aktuelle Kandidaten",
                "group_type": "application_wave",
            },
        )
        assert group.status_code == 201
        group_id = group.json()["id"]
        assert (
            client.post(
                f"/api/groups/{group_id}/memberships",
                json={"opportunity_id": target_id},
            ).status_code
            == 200
        )
        decisions_before = client.get(f"/api/opportunities/{target_id}/decisions").json()
        assert decisions_before[-1]["resulting_status"] == "shortlisted"

        update_prompt = client.post(
            "/api/prompts/update",
            json={
                "mode": "opportunity_update",
                "as_of_date": "2026-08-19",
                "selected_ids": [target_id],
            },
        )
        assert update_prompt.status_code == 200, update_prompt.text
        update = update_prompt.json()
        applied_update = client.post(
            "/api/imports/text",
            json={"content": json.dumps(update_bundle(update), ensure_ascii=False)},
        )
        assert applied_update.status_code == 200
        assert applied_update.json()["status"] == "applied", applied_update.json()[
            "issues"
        ]
        assert (
            applied_update.json()["prompt_context_ref"]
            == update["prompt_context_ref"]
        )

        assert client.get(f"/api/opportunities/{target_id}/note").json()[
            "content"
        ].startswith("Gute Java-/Maven-Passung")
        assert (
            client.get(f"/api/opportunities/{target_id}").json()["tracking_status"]
            == "shortlisted"
        )
        assert (
            client.get(f"/api/opportunities/{target_id}/decisions").json()
            == decisions_before
        )
        assert (
            client.get(f"/api/groups/{group_id}").json()["memberships"][0][
                "opportunity_id"
            ]
            == target_id
        )
        detail_after = client.get(f"/api/opportunities/{target_id}").json()
        assert any(
            posting["source_reference"]["url"] == initial_source_url
            for posting in detail_after["postings"]
        )
        assert any(
            observation["evidence_summary"]
            == "Official posting still states hybrid work."
            for observation in detail_after["observations"]
        )

    with TestClient(create_app(settings)) as client:
        candidate_after_restart = client.get("/api/profiles/candidate")
        assert candidate_after_restart.status_code == 200
        assert (
            candidate_after_restart.json()["headline"] == "Junior Softwareentwickler"
        )
        profiles = client.get("/api/profiles/search").json()
        persisted_profile = next(
            profile for profile in profiles if profile["id"] == profile_id
        )
        assert persisted_profile["is_default"] is True
        assert persisted_profile["revision"] == 1

        note_after_restart = client.get(f"/api/opportunities/{target_id}/note").json()
        assert note_after_restart["content"].startswith("Gute Java-/Maven-Passung")
        detail = client.get(f"/api/opportunities/{target_id}").json()
        assert detail["tracking_status"] == "shortlisted"
        assert any(
            posting["source_reference"]["url"] == initial_source_url
            for posting in detail["postings"]
        )
        assert (
            client.get(f"/api/groups/{group_id}").json()["memberships"][0][
                "opportunity_id"
            ]
            == target_id
        )
        assert (
            client.get(f"/api/opportunities/{target_id}/decisions").json()[-1][
                "resulting_status"
            ]
            == "shortlisted"
        )
