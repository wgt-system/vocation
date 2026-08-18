from __future__ import annotations

import json
from pathlib import Path

from vocation.infrastructure.models import PromptRunModel
from vocation.infrastructure.prompt_context_repository import SqlAlchemyPromptContextSnapshotRepository

ROOT = Path(__file__).resolve().parents[2]


def search_payload(*, name: str = "Hamburg quality", limit: int = 5) -> dict:
    return {
        "name": name,
        "description": "Quality-first search profile",
        "target_roles": ["Junior Softwareentwickler"],
        "seniority_targets": ["junior"],
        "preferred_technologies": ["Java"],
        "acceptable_technologies": ["Python"],
        "avoided_technologies": [],
        "target_locations": ["Hamburg"],
        "work_models": ["hybrid"],
        "relocation_willing": False,
        "employment_types": ["full-time"],
        "preferred_industries": [],
        "avoided_industries": [],
        "preferred_company_characteristics": [],
        "avoided_company_characteristics": [],
        "salary_floor": None,
        "salary_target": None,
        "salary_currency": "EUR",
        "must_haves": ["Berufseinstieg möglich"],
        "must_not_haves": ["Senior-only"],
        "result_limit": limit,
        "criterion_policies": [],
    }


def create_profile(client) -> str:
    created = client.post("/api/profiles/search", json=search_payload())
    assert created.status_code == 201
    profile_id = created.json()["id"]
    assert client.post(f"/api/profiles/search/{profile_id}/default").status_code == 200
    return profile_id


def create_candidate(client) -> None:
    response = client.put(
        "/api/profiles/candidate",
        json={
            "headline": "Softwareentwickler",
            "summary": "B.Sc. Informatik mit Java-Erfahrung.",
            "skills": [{"name": "Java", "level": "strong", "notes": "Maven projects"}],
        },
    )
    assert response.status_code == 200


def prompt_context(client, prompt_run_id: str):
    database = client.app.state.database
    with database.session_factory() as session:
        run = session.get(PromptRunModel, prompt_run_id)
        assert run is not None
        assert run.prompt_context_ref is not None
        context_ref = run.prompt_context_ref
    repository = SqlAlchemyPromptContextSnapshotRepository(database.session_factory)
    context = repository.get(context_ref)
    assert context is not None
    return context


def valid_bundle() -> dict:
    return json.loads((ROOT / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8"))


def test_default_profile_and_candidate_are_snapshotted_at_exact_revisions(client) -> None:
    profile_id = create_profile(client)
    create_candidate(client)

    generated = client.post(
        "/api/prompts/initial",
        json={"search_profile": "", "constraints": [], "as_of_date": "2026-08-17"},
    )
    assert generated.status_code == 200
    context = prompt_context(client, generated.json()["prompt_run_id"])
    assert generated.headers["X-Prompt-Context-Ref"] == context.prompt_context_ref

    assert context.scope_type == "initial_market_research"
    assert context.scope_json["search_profile"]["id"] == profile_id
    assert context.scope_json["search_profile"]["revision"] == 1
    assert context.scope_json["candidate_profile"]["revision"] == 1
    assert context.scope_json["research_scope"] == {
        "type": "initial_market_research",
        "as_of_date": "2026-08-17",
        "search_profile": "Hamburg quality",
        "constraints": ["Must have: Berufseinstieg möglich", "Must not have: Senior-only"],
    }

    revised = search_payload(limit=3)
    assert client.put(f"/api/profiles/search/{profile_id}", json=revised).json()["revision"] == 2
    assert context.scope_json["search_profile"]["revision"] == 1
    assert context.scope_json["search_profile"]["snapshot"]["result_limit"] == 5


def test_candidate_profile_can_be_explicitly_excluded_from_prompt_context(client) -> None:
    profile_id = create_profile(client)
    create_candidate(client)

    generated = client.post(
        "/api/prompts/initial?include_candidate_profile=false",
        json={"search_profile": profile_id, "constraints": [], "as_of_date": "2026-08-17"},
    )
    assert generated.status_code == 200
    assert "Not included in this research run." in generated.json()["prompt_text"]
    context = prompt_context(client, generated.json()["prompt_run_id"])
    assert context.scope_json["candidate_profile"] is None


def test_linked_initial_import_requires_exact_generated_scope_and_persists_context(client) -> None:
    profile_id = create_profile(client)
    generated = client.post(
        "/api/prompts/initial?include_candidate_profile=false",
        json={"search_profile": profile_id, "constraints": [], "as_of_date": "2026-08-17"},
    )
    assert generated.status_code == 200
    prompt_run_id = generated.json()["prompt_run_id"]
    context = prompt_context(client, prompt_run_id)

    bundle = valid_bundle()
    bundle["bundle_id"] = "profile-aware-linked-import"
    bundle["research_scope"] = context.scope_json["research_scope"]
    response = client.post(
        f"/api/imports/text?prompt_run_id={prompt_run_id}",
        json={"content": json.dumps(bundle, ensure_ascii=False)},
    )
    assert response.status_code == 200
    report = response.json()
    assert report["status"] == "applied"
    assert report["prompt_context_ref"] == context.prompt_context_ref

    stored = client.get(f"/api/imports/{report['import_id']}").json()
    assert stored["prompt_context_ref"] == context.prompt_context_ref


def test_linked_initial_import_rejects_scope_mismatch(client) -> None:
    profile_id = create_profile(client)
    generated = client.post(
        "/api/prompts/initial",
        json={"search_profile": profile_id, "constraints": [], "as_of_date": "2026-08-17"},
    )
    prompt_run_id = generated.json()["prompt_run_id"]
    bundle = valid_bundle()
    bundle["bundle_id"] = "profile-aware-mismatch"
    bundle["research_scope"]["search_profile"] = "Different strategy"

    response = client.post(
        f"/api/imports/text?prompt_run_id={prompt_run_id}",
        json={"content": json.dumps(bundle, ensure_ascii=False)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["issues"][0]["code"] == "SCOPE_MISMATCH"


def test_legacy_initial_bundle_without_prompt_context_remains_supported(client) -> None:
    bundle = valid_bundle()
    response = client.post("/api/imports/text", json={"content": json.dumps(bundle, ensure_ascii=False)})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    assert response.json()["prompt_context_ref"] is None
