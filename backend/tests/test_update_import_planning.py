from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select
from tests.test_imports import import_bundle, valid_bundle
from vocation.infrastructure.models import (
    CompanyModel,
    DuplicateCaseModel,
    OpportunityDecisionModel,
    OpportunityModel,
    PersonalAssessmentModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptContextSubjectModel,
)

ROOT = Path(__file__).resolve().parents[2]


def load_update(name: str) -> dict:
    return json.loads((ROOT / "examples" / "updates" / name).read_text(encoding="utf-8"))


def snapshot(client, bundle: dict, subjects: list[tuple[str, str, str, bool]] = None) -> None:
    subjects = subjects or []
    with client.app.state.database.session_factory.begin() as session:
        session.add(
            PromptContextSnapshotModel(
                prompt_context_ref=bundle["prompt_context_ref"],
                scope_type=bundle["research_scope"]["type"],
                as_of_date=bundle["research_scope"]["as_of_date"],
                scope_json=json.dumps(bundle["research_scope"], sort_keys=True, separators=(",", ":")),
                fingerprint=(bundle["prompt_context_ref"] + "0" * 64)[:64],
                created_at=datetime.now(UTC),
            )
        )
        for correlation_ref, subject_type, subject_id, is_target in subjects:
            session.add(
                PromptContextSubjectModel(
                    prompt_context_ref=bundle["prompt_context_ref"],
                    correlation_ref=correlation_ref,
                    subject_type=subject_type,
                    subject_id=subject_id,
                    is_target=is_target,
                )
            )


def codes(result) -> set[str]:
    return {issue.code for issue in result.issues}


def row_counts(client) -> dict[str, int]:
    models = {
        "companies": CompanyModel,
        "opportunities": OpportunityModel,
        "postings": PostingModel,
        "duplicate_cases": DuplicateCaseModel,
        "personal_assessments": PersonalAssessmentModel,
        "decisions": OpportunityDecisionModel,
    }
    with client.app.state.database.session_factory() as session:
        return {name: session.scalar(select(func.count()).select_from(model)) for name, model in models.items()}


def test_unknown_snapshot_and_scope_mismatch_are_blockers_without_writes(client) -> None:
    bundle = load_update("full-update-valid.json")
    before = row_counts(client)
    unknown = client.app.state.update_import_planner.plan(bundle)
    assert unknown.plan is None
    assert codes(unknown) == {"UNKNOWN_PROMPT_CONTEXT"}
    snapshot(client, bundle)
    altered = copy.deepcopy(bundle)
    altered["research_scope"]["as_of_date"] = "2026-08-07"
    mismatch = client.app.state.update_import_planner.plan(altered)
    assert mismatch.plan is None
    assert codes(mismatch) == {"SCOPE_MISMATCH"}
    assert row_counts(client) == before


def test_full_update_plans_new_subjects_and_duplicate_evidence_read_only(client) -> None:
    bundle = load_update("full-update-valid.json")
    snapshot(client, bundle)
    before = row_counts(client)
    result = client.app.state.update_import_planner.plan(bundle)
    assert not result.issues
    assert result.plan is not None
    assert {item.action for item in result.plan.companies} == {"create"}
    assert {item.action for item in result.plan.opportunities} == {"create"}
    assert {item.action for item in result.plan.postings} == {"create"}
    assert result.plan.duplicate_cases[0].action == "create"
    assert row_counts(client) == before


def test_company_update_plans_allowed_new_children_but_not_company(client) -> None:
    initial = valid_bundle()
    assert import_bundle(client, initial).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        company_id = session.scalar(select(CompanyModel)).id
    bundle = load_update("company-update-valid.json")
    snapshot(client, bundle, [("company-reference-1", "company", company_id, True)])
    result = client.app.state.update_import_planner.plan(bundle)
    assert not result.issues
    assert result.plan.companies[0].action == "reuse"
    assert result.plan.opportunities[0].action == "create"
    assert result.plan.postings[0].action == "create"

    forbidden = copy.deepcopy(bundle)
    forbidden["companies"].append(
        {
            "id": "company-new",
            "canonical_name": "Forbidden",
            "source_reference_id": "ref-company",
            "observed_at": "2026-08-08T09:00:00Z",
        }
    )
    rejected = client.app.state.update_import_planner.plan(forbidden)
    assert "SCOPE_VIOLATION" in codes(rejected)


def test_opportunity_update_and_gap_filling_scope_rules(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    opportunity_bundle = load_update("opportunity-update-valid.json")
    snapshot(
        client,
        opportunity_bundle,
        [
            ("company-reference-2", "company", company.id, False),
            ("opportunity-reference-1", "opportunity", opportunity.id, True),
            ("posting-reference-1", "posting", posting.id, True),
        ],
    )
    result = client.app.state.update_import_planner.plan(opportunity_bundle)
    assert not result.issues
    assert result.plan.opportunities[0].action == "reuse"
    assert result.plan.postings[0].action == "reuse"

    gap = load_update("gap-filling-valid.json")
    snapshot(
        client,
        gap,
        [
            ("company-reference-3", "company", company.id, False),
            ("opportunity-reference-2", "opportunity", opportunity.id, True),
            ("posting-reference-2", "posting", posting.id, False),
        ],
    )
    accepted = client.app.state.update_import_planner.plan(gap)
    assert not accepted.issues
    unrequested = copy.deepcopy(gap)
    unrequested["observations"][0]["type"] = "task"
    rejected = client.app.state.update_import_planner.plan(unrequested)
    assert "SCOPE_MISMATCH" not in codes(rejected)
    assert "SCOPE_VIOLATION" in codes(rejected)


def test_correlation_ownership_and_context_only_evidence_are_blockers(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    bundle = load_update("opportunity-update-valid.json")
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company.id, False),
            ("opportunity-reference-1", "opportunity", opportunity.id, False),
            ("posting-reference-1", "posting", posting.id, False),
        ],
    )
    context_evidence = client.app.state.update_import_planner.plan(bundle)
    assert "SCOPE_VIOLATION" in codes(context_evidence)

    wrong_company = copy.deepcopy(bundle)
    wrong_company["opportunities"][0]["company_id"] = "company-context"
    wrong_company["companies"].append({"id": "company-context-2", "correlation_ref": "company-reference-2"})
    wrong_company["opportunities"][0]["company_id"] = "company-context-2"
    ownership = client.app.state.update_import_planner.plan(wrong_company)
    assert "RELATIONSHIP_MISMATCH" in codes(ownership)


def test_gap_requests_and_assessments_are_checked(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    bundle = load_update("gap-filling-valid.json")
    snapshot(
        client,
        bundle,
        [
            ("company-reference-3", "company", company.id, False),
            ("opportunity-reference-2", "opportunity", opportunity.id, True),
            ("posting-reference-2", "posting", posting.id, False),
        ],
    )
    unrequested = copy.deepcopy(bundle)
    unrequested["assessments"][0]["criterion_id"] = "junior_suitability"
    result = client.app.state.update_import_planner.plan(unrequested)
    assert "SCOPE_VIOLATION" in codes(result)


def test_identity_reuse_scope_conflict_and_duplicate_reuse(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    bundle = load_update("opportunity-update-valid.json")
    bundle["postings"][0]["identity_evidence"]["external_posting_id"] = "EX-123"
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company.id, True),
            ("opportunity-reference-1", "opportunity", opportunity.id, True),
            ("posting-reference-1", "posting", posting.id, True),
        ],
    )
    result = client.app.state.update_import_planner.plan(bundle)
    assert not result.issues
    assert result.plan.postings[0].action == "reuse"

    duplicate_bundle = load_update("full-update-valid.json")
    duplicate_bundle["postings"][0]["external_posting_id"] = "EX-123"
    duplicate_bundle["sources"][0]["base_url"] = "https://example.com/careers"
    snapshot(client, duplicate_bundle, [("posting-target", "posting", posting.id, False)])
    conflict = client.app.state.update_import_planner.plan(duplicate_bundle)
    assert "SCOPE_VIOLATION" in codes(conflict)
    assert row_counts(client)["postings"] == 1
