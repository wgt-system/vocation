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
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityDecisionModel,
    OpportunityModel,
    PersonalAssessmentModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptContextSubjectModel,
    ResearchImportModel,
    SourceModel,
    SourceReferenceModel,
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
        "research_imports": ResearchImportModel,
        "sources": SourceModel,
        "source_references": SourceReferenceModel,
        "companies": CompanyModel,
        "opportunities": OpportunityModel,
        "postings": PostingModel,
        "observations": ObservationModel,
        "external_assessments": ExternalAssessmentModel,
        "duplicate_cases": DuplicateCaseModel,
        "personal_assessments": PersonalAssessmentModel,
        "opportunity_decisions": OpportunityDecisionModel,
    }
    with client.app.state.database.session_factory() as session:
        return {name: session.scalar(select(func.count()).select_from(model)) for name, model in models.items()}


def import_two_initial_bundles(client) -> tuple[dict, dict]:
    first = valid_bundle()
    second = json.loads(json.dumps(first).replace("example", "second"))
    assert import_bundle(client, first).json()["status"] == "applied"
    assert import_bundle(client, second).json()["status"] == "applied"
    return first, second


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


def test_unknown_and_wrong_type_correlations_are_distinct_blockers(client) -> None:
    bundle = load_update("opportunity-update-valid.json")
    snapshot(client, bundle, [("company-reference-2", "company", "missing", True)])
    unknown = copy.deepcopy(bundle)
    unknown["companies"][0]["correlation_ref"] = "not-in-snapshot"
    result = client.app.state.update_import_planner.plan(unknown)
    assert codes(result) == {"UNKNOWN_CORRELATION_REFERENCE"}

    wrong_type = copy.deepcopy(bundle)
    wrong_type["prompt_context_ref"] = "prompt-snapshot-wrong-type"
    snapshot(client, wrong_type, [("company-reference-2", "opportunity", "wrong-type", True)])
    result = client.app.state.update_import_planner.plan(wrong_type)
    assert codes(result) == {"UNKNOWN_CORRELATION_REFERENCE"}


def test_existing_opportunity_ownership_mismatch_is_scope_violation(client) -> None:
    first, second = import_two_initial_bundles(client)
    bundle = load_update("opportunity-update-valid.json")
    bundle["postings"] = []
    with client.app.state.database.session_factory() as session:
        company_a = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-example"))
        company_b = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-second"))
        opportunity_a = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-example"))
    assert company_a and company_b and opportunity_a
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company_b.id, True),
            ("opportunity-reference-1", "opportunity", opportunity_a.id, True),
        ],
    )
    result = client.app.state.update_import_planner.plan(bundle)
    assert codes(result) == {"SCOPE_VIOLATION"}
    assert first["bundle_id"] != second["bundle_id"]


def test_existing_posting_ownership_mismatch_is_identity_conflict(client) -> None:
    import_two_initial_bundles(client)
    bundle = load_update("opportunity-update-valid.json")
    with client.app.state.database.session_factory() as session:
        company_b = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-second"))
        opportunity_b = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-second"))
        posting_a = session.scalar(select(PostingModel).where(PostingModel.bundle_local_id == "post-example"))
    assert company_b and opportunity_b and posting_a
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company_b.id, True),
            ("opportunity-reference-1", "opportunity", opportunity_b.id, True),
            ("posting-reference-1", "posting", posting_a.id, True),
        ],
    )
    result = client.app.state.update_import_planner.plan(bundle)
    assert codes(result) == {"IDENTITY_CONFLICT"}


def test_opportunity_update_can_create_posting_but_not_opportunity(client) -> None:
    import_bundle(client, valid_bundle())
    bundle = load_update("opportunity-update-valid.json")
    bundle["postings"][0].pop("correlation_ref")
    bundle["postings"][0].pop("identity_evidence")
    bundle["postings"][0]["source_reference_id"] = "ref-posting"
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
    assert company and opportunity
    snapshot(
        client,
        bundle,
        [("company-reference-2", "company", company.id, False), ("opportunity-reference-1", "opportunity", opportunity.id, True)],
    )
    result = client.app.state.update_import_planner.plan(bundle)
    assert not result.issues
    assert result.plan.postings[0].action == "create"

    forbidden = copy.deepcopy(bundle)
    forbidden["opportunities"].append(
        {"id": "new-opportunity", "company_id": "company-context", "canonical_title": "Forbidden"}
    )
    rejected = client.app.state.update_import_planner.plan(forbidden)
    assert "SCOPE_VIOLATION" in codes(rejected)


def test_gap_filling_cannot_plan_new_subjects(client) -> None:
    import_bundle(client, valid_bundle())
    bundle = load_update("gap-filling-valid.json")
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    assert company and opportunity and posting
    snapshot(
        client,
        bundle,
        [
            ("company-reference-3", "company", company.id, True),
            ("opportunity-reference-2", "opportunity", opportunity.id, True),
            ("posting-reference-2", "posting", posting.id, True),
        ],
    )
    for collection in ("companies", "opportunities", "postings"):
        attempted = copy.deepcopy(bundle)
        attempted[collection][0].pop("correlation_ref")
        if collection == "postings":
            attempted[collection][0]["source_reference_id"] = "ref-gap"
        result = client.app.state.update_import_planner.plan(attempted)
        assert "SCOPE_VIOLATION" in codes(result)


def test_posting_identity_conflicts_and_deterministic_reuse(client) -> None:
    import_two_initial_bundles(client)
    bundle = load_update("opportunity-update-valid.json")
    with client.app.state.database.session_factory() as session:
        company_a = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-example"))
        opportunity_a = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-example"))
        posting_a = session.scalar(select(PostingModel).where(PostingModel.bundle_local_id == "post-example"))
        posting_b = session.scalar(select(PostingModel).where(PostingModel.bundle_local_id == "post-second"))
    assert company_a and opportunity_a and posting_a and posting_b
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company_a.id, True),
            ("opportunity-reference-1", "opportunity", opportunity_a.id, True),
            ("posting-reference-1", "posting", posting_a.id, True),
        ],
    )
    conflicting = copy.deepcopy(bundle)
    conflicting["sources"][0].update({"type": "company_careers", "base_url": "https://second.com/careers"})
    conflicting["source_references"][0]["url"] = "https://second.com/careers/junior-dev"
    conflicting["postings"][0]["identity_evidence"]["external_posting_id"] = "EX-123"
    result = client.app.state.update_import_planner.plan(conflicting)
    assert "IDENTITY_CONFLICT" in codes(result)

    reuse = copy.deepcopy(bundle)
    reuse["postings"][0].pop("correlation_ref")
    reuse["postings"][0].pop("identity_evidence")
    reuse["source_references"][0].update({"url": "https://example.com/careers/junior-dev"})
    reuse["sources"][0].update({"type": "company_careers", "base_url": "https://example.com/careers"})
    reuse["postings"][0]["source_reference_id"] = "ref-posting"
    reuse["postings"][0]["external_posting_id"] = "EX-123"
    result = client.app.state.update_import_planner.plan(reuse)
    assert not result.issues
    assert result.plan.postings[0].action == "reuse"

    ownership = copy.deepcopy(reuse)
    ownership["prompt_context_ref"] = "prompt-snapshot-posting-ownership"
    ownership["sources"][0].update({"type": "company_careers", "base_url": "https://second.com/careers"})
    ownership["source_references"][0]["url"] = "https://second.com/careers/junior-dev"
    snapshot(
        client,
        ownership,
        [
            ("company-reference-2", "company", company_a.id, True),
            ("opportunity-reference-1", "opportunity", opportunity_a.id, True),
            ("posting-reference-1", "posting", posting_b.id, True),
        ],
    )
    result = client.app.state.update_import_planner.plan(ownership)
    assert "IDENTITY_CONFLICT" in codes(result)

    repeated = copy.deepcopy(reuse)
    repeated["postings"].append(copy.deepcopy(repeated["postings"][0]))
    repeated["postings"][1]["id"] = "posting-second-local"
    result = client.app.state.update_import_planner.plan(repeated)
    assert "IDENTITY_CONFLICT" in codes(result)


def test_duplicate_case_reuse_same_subject_and_context_only_blockers(client) -> None:
    import_two_initial_bundles(client)
    bundle = load_update("full-update-valid.json")
    bundle["postings"] = []
    bundle["observations"] = []
    bundle["assessments"] = []
    with client.app.state.database.session_factory() as session:
        company_a = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-example"))
        opportunity_a = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-example"))
        opportunity_b = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-second"))
    assert company_a and opportunity_a and opportunity_b
    with client.app.state.database.session_factory.begin() as session:
        session.get(OpportunityModel, opportunity_b.id).company_id = company_a.id
    bundle["companies"][0]["correlation_ref"] = "company-a"
    bundle["opportunities"][0]["correlation_ref"] = "opportunity-a"
    bundle["opportunities"][1]["correlation_ref"] = "opportunity-b"
    bundle["possible_duplicates"][0]["left_subject_id"] = "opportunity-other"
    bundle["possible_duplicates"][0]["right_subject_id"] = "opportunity-new"
    snapshot(
        client,
        bundle,
        [
            ("company-a", "company", company_a.id, True),
            ("opportunity-a", "opportunity", opportunity_a.id, True),
            ("opportunity-b", "opportunity", opportunity_b.id, True),
        ],
    )
    with client.app.state.database.session_factory.begin() as session:
        research_import = session.scalar(select(ResearchImportModel))
        left_subject_id, right_subject_id = sorted((opportunity_a.id, opportunity_b.id))
        session.add(
            DuplicateCaseModel(
                id="existing-case",
                research_import_id=research_import.id,
                subject_type="opportunity",
                left_subject_id=left_subject_id,
                right_subject_id=right_subject_id,
                evidence_summary="existing",
                confidence=0.4,
                created_at=datetime.now(UTC),
            )
        )
    assert client.app.state.duplicate_case_service.repository.find_by_pair(
        "opportunity", opportunity_a.id, opportunity_b.id
    )
    before = row_counts(client)
    result = client.app.state.update_import_planner.plan(bundle)
    assert not result.issues
    assert result.plan.duplicate_cases[0].action == "reuse"
    assert row_counts(client) == before

    same_subject = copy.deepcopy(bundle)
    same_subject["opportunities"][1]["correlation_ref"] = "opportunity-a"
    result = client.app.state.update_import_planner.plan(same_subject)
    assert "INVALID_DUPLICATE_EVIDENCE" in codes(result)

    context_only = copy.deepcopy(bundle)
    context_only["prompt_context_ref"] = "prompt-snapshot-full-context-only"
    snapshot(
        client,
        context_only,
        [
            ("company-a", "company", company_a.id, True),
            ("opportunity-a", "opportunity", opportunity_a.id, True),
            ("opportunity-b", "opportunity", opportunity_b.id, False),
        ],
    )
    result = client.app.state.update_import_planner.plan(context_only)
    assert "SCOPE_VIOLATION" in codes(result)
