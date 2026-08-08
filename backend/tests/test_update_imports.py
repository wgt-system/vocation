from __future__ import annotations

import copy
import json

import pytest
from sqlalchemy import func, select
from tests.test_imports import import_bundle, valid_bundle
from tests.test_update_import_planning import load_update, row_counts, snapshot
from vocation.infrastructure import bundle_repository
from vocation.infrastructure.models import (
    CompanyModel,
    DuplicateCaseModel,
    DuplicateCaseSourceReferenceModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    ResearchImportModel,
    SourceModel,
    SourceReferenceModel,
)


def post_update(client, bundle: dict) -> dict:
    return client.post("/api/imports/text", json={"content": json.dumps(bundle)}).json()


def persisted_subjects(client) -> tuple[CompanyModel, OpportunityModel, PostingModel]:
    with client.app.state.database.session_factory() as session:
        company = session.scalar(select(CompanyModel))
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
    assert company and opportunity and posting
    return company, opportunity, posting


def import_two_initial_bundles(client) -> None:
    first = valid_bundle()
    second = json.loads(json.dumps(first).replace("example", "second"))
    assert import_bundle(client, first).json()["status"] == "applied"
    assert import_bundle(client, second).json()["status"] == "applied"


def test_version_dispatch_and_initial_regression(client) -> None:
    initial = import_bundle(client, valid_bundle()).json()
    assert initial["status"] == "applied"

    unsupported = valid_bundle()
    unsupported["bundle_version"] = "9.0"
    report = import_bundle(client, unsupported).json()
    assert report["status"] == "rejected"
    assert {issue["code"] for issue in report["issues"]} == {"UNSUPPORTED_BUNDLE_VERSION"}

    missing = valid_bundle()
    del missing["bundle_version"]
    report = import_bundle(client, missing).json()
    assert report["status"] == "rejected"
    assert {issue["code"] for issue in report["issues"]} == {"UNSUPPORTED_BUNDLE_VERSION"}

    update_scope_as_v1 = load_update("full-update-valid.json")
    update_scope_as_v1["bundle_version"] = "1.0"
    report = import_bundle(client, update_scope_as_v1).json()
    assert report["status"] == "rejected"


def test_full_update_materializes_plan_and_counts(client) -> None:
    bundle = load_update("full-update-valid.json")
    snapshot(client, bundle)
    before = row_counts(client)
    report = post_update(client, bundle)
    assert report["status"] == "applied", report["issues"]
    assert report["counts"] == {
        "sources_created": 1,
        "source_references_created": 1,
        "companies_created": 1,
        "companies_reused": 0,
        "opportunities_created": 2,
        "opportunities_reused": 0,
        "postings_created": 1,
        "postings_reused": 0,
        "observations_created": 1,
        "assessments_created": 1,
        "duplicate_cases_created": 1,
        "duplicate_cases_reused": 0,
    }
    assert row_counts(client)["companies"] == before["companies"] + 1
    assert row_counts(client)["opportunities"] == before["opportunities"] + 2
    assert row_counts(client)["postings"] == before["postings"] + 1
    assert row_counts(client)["observations"] == before["observations"] + 1
    assert row_counts(client)["external_assessments"] == before["external_assessments"] + 1
    assert row_counts(client)["duplicate_cases"] == before["duplicate_cases"] + 1
    with client.app.state.database.session_factory() as session:
        duplicate = session.scalar(select(DuplicateCaseModel).where(DuplicateCaseModel.research_import_id == report["import_id"]))
        assert duplicate is not None
        assert session.scalar(
            select(func.count()).select_from(DuplicateCaseSourceReferenceModel).where(
                DuplicateCaseSourceReferenceModel.duplicate_case_id == duplicate.id
            )
        ) == 1
        link = session.scalar(
            select(DuplicateCaseSourceReferenceModel).where(
                DuplicateCaseSourceReferenceModel.duplicate_case_id == duplicate.id
            )
        )
        source_reference = session.get(SourceReferenceModel, link.source_reference_id)
        assert source_reference.import_id == report["import_id"]


def test_full_update_file_entry_point(client) -> None:
    bundle = load_update("full-update-valid.json")
    snapshot(client, bundle)
    response = client.post(
        "/api/imports/file",
        files={"file": ("update.json", json.dumps(bundle).encode("utf-8"), "application/json")},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "applied"


def test_update_reuses_posting_and_preserves_original_provenance(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    company, opportunity, posting = persisted_subjects(client)
    bundle = load_update("opportunity-update-valid.json")
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company.id, True),
            ("opportunity-reference-1", "opportunity", opportunity.id, True),
            ("posting-reference-1", "posting", posting.id, True),
        ],
    )
    original_posting = {
        "source_reference_id": posting.source_reference_id,
        "stable_key": posting.stable_key,
        "canonical_url": posting.canonical_url,
        "external_posting_id": posting.external_posting_id,
        "title": posting.title,
        "company_id": posting.company_id,
        "opportunity_id": posting.opportunity_id,
        "import_id": posting.import_id,
    }
    before = row_counts(client)
    report = post_update(client, bundle)
    assert report["status"] == "applied", report["issues"]
    assert report["counts"]["postings_reused"] == 1
    assert report["counts"]["postings_created"] == 0
    assert row_counts(client)["postings"] == before["postings"]
    assert row_counts(client)["observations"] == before["observations"] + 1
    with client.app.state.database.session_factory() as session:
        unchanged = session.get(PostingModel, posting.id)
        assert {field: getattr(unchanged, field) for field in original_posting} == original_posting
        assert session.scalar(select(func.count()).select_from(SourceModel)) == before["sources"] + 1
        assert session.scalar(select(func.count()).select_from(SourceReferenceModel)) == before["source_references"] + 1
        observation = session.scalar(select(ObservationModel).where(ObservationModel.import_id == report["import_id"]))
        assert observation.subject_id == opportunity.id
        assert observation.source_reference_id != original_posting["source_reference_id"]


def test_company_update_creates_scoped_children(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    company, _, _ = persisted_subjects(client)
    bundle = load_update("company-update-valid.json")
    snapshot(client, bundle, [("company-reference-1", "company", company.id, True)])
    report = post_update(client, bundle)
    assert report["status"] == "applied"
    assert report["counts"]["companies_reused"] == 1
    assert report["counts"]["opportunities_created"] == 1
    assert report["counts"]["postings_created"] == 1


def test_gap_filling_appends_requested_evidence_without_core_mutation(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    company, opportunity, posting = persisted_subjects(client)
    bundle = load_update("gap-filling-valid.json")
    snapshot(
        client,
        bundle,
        [
            ("company-reference-3", "company", company.id, False),
            ("opportunity-reference-2", "opportunity", opportunity.id, True),
            ("posting-reference-2", "posting", posting.id, True),
        ],
    )
    before = row_counts(client)
    report = post_update(client, bundle)
    assert report["status"] == "applied"
    assert row_counts(client)["companies"] == before["companies"]
    assert row_counts(client)["opportunities"] == before["opportunities"]
    assert row_counts(client)["postings"] == before["postings"]
    assert row_counts(client)["observations"] == before["observations"] + 1
    assert row_counts(client)["external_assessments"] == before["external_assessments"] + 1


def test_update_preserves_personal_assessments_and_decisions(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    created = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "personal"},
    )
    assert created.status_code == 201
    revised = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal/{created.json()['id']}/revisions",
        json={"value": 5, "reasoning": "revised"},
    )
    assert revised.status_code == 201
    assert client.post(f"/api/opportunities/{opportunity_id}/status", json={"status": "shortlisted"}).status_code == 200
    before_assessments = client.get(f"/api/opportunities/{opportunity_id}/assessments/personal/history").json()
    before_decisions = client.get(f"/api/opportunities/{opportunity_id}/decisions").json()
    before_status = client.get("/api/opportunities").json()[0]["tracking_status"]

    company, opportunity, posting = persisted_subjects(client)
    bundle = load_update("opportunity-update-valid.json")
    snapshot(
        client,
        bundle,
        [
            ("company-reference-2", "company", company.id, True),
            ("opportunity-reference-1", "opportunity", opportunity.id, True),
            ("posting-reference-1", "posting", posting.id, True),
        ],
    )
    assert post_update(client, bundle)["status"] == "applied"
    assert client.get(f"/api/opportunities/{opportunity_id}/assessments/personal/history").json() == before_assessments
    assert client.get(f"/api/opportunities/{opportunity_id}/decisions").json() == before_decisions
    assert client.get("/api/opportunities").json()[0]["tracking_status"] == before_status


def test_update_reuses_existing_duplicate_case_without_modification(client) -> None:
    import_two_initial_bundles(client)
    with client.app.state.database.session_factory() as session:
        company_a = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-example"))
        company_b = session.scalar(select(CompanyModel).where(CompanyModel.bundle_local_id == "cmp-second"))
        opportunity_a = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-example"))
        opportunity_b = session.scalar(select(OpportunityModel).where(OpportunityModel.bundle_local_id == "opp-second"))
        reference = session.scalar(select(SourceReferenceModel).where(SourceReferenceModel.bundle_local_id == "ref-posting"))
        research_import = session.scalar(select(ResearchImportModel))
    assert company_a and company_b and opportunity_a and opportunity_b and reference and research_import
    with client.app.state.database.session_factory.begin() as session:
        session.get(OpportunityModel, opportunity_b.id).company_id = company_a.id
        left_id, right_id = sorted((opportunity_a.id, opportunity_b.id))
        existing_case = DuplicateCaseModel(
            id="existing-duplicate-case",
            research_import_id=research_import.id,
            subject_type="opportunity",
            left_subject_id=left_id,
            right_subject_id=right_id,
            evidence_summary="Persisted duplicate evidence",
            confidence=0.75,
            created_at=research_import.created_at,
        )
        session.add(existing_case)
        session.flush()
        session.add(
            DuplicateCaseSourceReferenceModel(
                duplicate_case_id=existing_case.id,
                source_reference_id=reference.id,
            )
        )

    bundle = load_update("full-update-valid.json")
    bundle["postings"] = []
    bundle["observations"] = []
    bundle["assessments"] = []
    bundle["companies"][0]["correlation_ref"] = "company-reference-a"
    for field in ("canonical_name", "source_reference_id", "observed_at", "evidence_summary"):
        bundle["companies"][0].pop(field, None)
    bundle["opportunities"][0]["correlation_ref"] = "opportunity-reference-a"
    bundle["opportunities"][1]["correlation_ref"] = "opportunity-reference-b"
    for opportunity_item in bundle["opportunities"]:
        for field in ("canonical_title", "source_reference_id", "observed_at", "evidence_summary", "work_locations"):
            opportunity_item.pop(field, None)
    bundle["possible_duplicates"][0]["left_subject_id"] = "opportunity-other"
    bundle["possible_duplicates"][0]["right_subject_id"] = "opportunity-new"
    snapshot(
        client,
        bundle,
        [
            ("company-reference-a", "company", company_a.id, True),
            ("opportunity-reference-a", "opportunity", opportunity_a.id, True),
            ("opportunity-reference-b", "opportunity", opportunity_b.id, True),
        ],
    )
    with client.app.state.database.session_factory() as session:
        before_case = session.get(DuplicateCaseModel, "existing-duplicate-case")
        before_links = [
            link.source_reference_id
            for link in session.scalars(
                select(DuplicateCaseSourceReferenceModel).where(
                    DuplicateCaseSourceReferenceModel.duplicate_case_id == before_case.id
                )
            )
        ]
    before_count = row_counts(client)["duplicate_cases"]
    report = post_update(client, bundle)
    assert report["status"] == "applied", report["issues"]
    assert report["counts"]["duplicate_cases_reused"] == 1
    assert report["counts"]["duplicate_cases_created"] == 0
    assert row_counts(client)["duplicate_cases"] == before_count
    with client.app.state.database.session_factory() as session:
        after_case = session.get(DuplicateCaseModel, "existing-duplicate-case")
        after_links = [
            link.source_reference_id
            for link in session.scalars(
                select(DuplicateCaseSourceReferenceModel).where(
                    DuplicateCaseSourceReferenceModel.duplicate_case_id == after_case.id
                )
            )
        ]
        assert after_case.research_import_id == before_case.research_import_id
        assert after_case.evidence_summary == before_case.evidence_summary
        assert after_case.confidence == before_case.confidence
        assert after_case.created_at == before_case.created_at
        assert after_links == before_links


def test_update_idempotency_and_rejected_planner_blocker(client) -> None:
    bundle = load_update("full-update-valid.json")
    snapshot(client, bundle)
    first = post_update(client, bundle)
    after_first = row_counts(client)
    second = post_update(client, copy.deepcopy(bundle))
    assert first["status"] == "applied"
    assert second["status"] == "duplicate"
    assert second["duplicate_of_import_id"] == first["import_id"]
    assert row_counts(client) == after_first

    rejected = load_update("full-update-valid.json")
    rejected["prompt_context_ref"] = "prompt-snapshot-rejected"
    snapshot(client, rejected)
    rejected["research_scope"]["as_of_date"] = "2026-08-07"
    before = row_counts(client)
    report = post_update(client, rejected)
    assert report["status"] == "rejected"
    assert {issue["code"] for issue in report["issues"]} == {"SCOPE_MISMATCH"}
    after = row_counts(client)
    assert after["sources"] == before["sources"]
    assert after["source_references"] == before["source_references"]
    assert after["companies"] == before["companies"]
    assert after["opportunities"] == before["opportunities"]
    assert after["postings"] == before["postings"]
    assert after["observations"] == before["observations"]
    assert after["external_assessments"] == before["external_assessments"]
    assert after["duplicate_cases"] == before["duplicate_cases"]


def test_update_apply_rolls_back_staged_rows(client, monkeypatch: pytest.MonkeyPatch) -> None:
    bundle = load_update("full-update-valid.json")
    snapshot(client, bundle)
    planner = client.app.state.update_import_planner
    result = planner.plan(bundle)
    assert not result.issues and result.plan
    repository = client.app.state.database
    import_repo = client.app.state.import_service.repository
    original_datetime = bundle_repository._datetime
    calls = 0

    def fail_after_source_rows(value: str):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("forced update apply failure")
        return original_datetime(value)

    monkeypatch.setattr(bundle_repository, "_datetime", fail_after_source_rows)
    before = row_counts(client)
    with pytest.raises(RuntimeError, match="forced update apply failure"):
        import_repo.apply_update(bundle, result.plan, "f" * 64)
    assert row_counts(client) == before
    with repository.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(ResearchImportModel)) == before["research_imports"]
        assert session.scalar(select(func.count()).select_from(DuplicateCaseModel)) == before["duplicate_cases"]
