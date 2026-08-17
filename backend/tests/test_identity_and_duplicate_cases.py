from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from vocation.application.duplicate_cases import DuplicateDecisionConflictError
from vocation.domain.research_bundle import PostingIdentityConflictError, PostingIdentityInput, canonical_subject_pair
from vocation.infrastructure.duplicate_case_decision_model import DuplicateCaseDecisionModel
from vocation.infrastructure.models import (
    DuplicateCaseModel,
    OpportunityModel,
    PersonalAssessmentModel,
    PostingModel,
    SourceReferenceModel,
)

ROOT = Path(__file__).resolve().parents[2]


def valid_bundle() -> dict:
    return json.loads((ROOT / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8"))


def import_bundle(client, bundle: dict):
    return client.post("/api/imports/text", json={"content": json.dumps(bundle, ensure_ascii=False)})


def imported_postings(client):
    first = valid_bundle()
    assert import_bundle(client, first).json()["status"] == "applied"
    second = copy.deepcopy(first)
    second["bundle_id"] = "example-initial-002"
    second["generated_at"] = "2026-08-07T17:00:00Z"
    second["source_references"][0]["id"] = "ref-posting-2"
    second["source_references"][0]["url"] = "https://example.com/careers/senior-dev"
    second["companies"][0]["id"] = "cmp-example-2"
    second["companies"][0]["source_reference_id"] = "ref-posting-2"
    second["opportunities"][0]["id"] = "opp-example-2"
    second["opportunities"][0]["company_id"] = "cmp-example-2"
    second["opportunities"][0]["source_reference_id"] = "ref-posting-2"
    second["opportunities"][0]["work_locations"][0]["source_reference_id"] = "ref-posting-2"
    second["postings"][0]["id"] = "post-example-2"
    second["postings"][0]["company_id"] = "cmp-example-2"
    second["postings"][0]["opportunity_id"] = "opp-example-2"
    second["postings"][0]["source_reference_id"] = "ref-posting-2"
    second["postings"][0]["external_posting_id"] = "EX-456"
    second["observations"][0]["subject_id"] = "post-example-2"
    second["observations"][0]["source_reference_id"] = "ref-posting-2"
    second["assessments"][0]["subject_id"] = "opp-example-2"
    second["assessments"][0]["source_reference_ids"] = ["ref-posting-2"]
    assert import_bundle(client, second).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        return session.scalars(select(PostingModel).order_by(PostingModel.stable_key)).all()


def test_posting_identity_resolver_covers_deterministic_and_correlation_cases(client) -> None:
    postings = imported_postings(client)
    source = valid_bundle()["sources"][0]
    resolver = client.app.state.posting_identity_resolver
    first, second = postings

    by_external = resolver.resolve(PostingIdentityInput(source, "https://example.com/careers/new", external_posting_id="EX-123"))
    assert by_external.posting.posting_id == first.id
    assert by_external.kind == "external_posting_id"
    by_url = resolver.resolve(PostingIdentityInput(source, first.canonical_url))
    assert by_url.posting.posting_id == first.id
    assert by_url.kind == "url"
    unresolved = resolver.resolve(PostingIdentityInput(source, "https://example.com/careers/unknown"))
    assert unresolved.posting is None
    assert unresolved.kind == "unresolved"
    correlated = resolver.resolve(
        PostingIdentityInput(source, second.canonical_url, external_posting_id="EX-999", correlated_posting_id=second.id)
    )
    assert correlated.posting.posting_id == second.id
    assert correlated.kind == "correlation"
    with pytest.raises(PostingIdentityConflictError) as error:
        resolver.resolve(PostingIdentityInput(source, first.canonical_url, correlated_posting_id=second.id))
    assert error.value.code == "IDENTITY_CONFLICT"


def test_posting_identity_conflicts_and_resolver_are_read_only(client) -> None:
    postings = imported_postings(client)
    source = valid_bundle()["sources"][0]
    resolver = client.app.state.posting_identity_resolver
    first, second = postings
    before = (first.stable_key, first.canonical_url)
    with pytest.raises(PostingIdentityConflictError):
        resolver.resolve(PostingIdentityInput(source, second.canonical_url, external_posting_id="EX-123"))
    with pytest.raises(PostingIdentityConflictError):
        resolver.resolve(PostingIdentityInput(source, second.canonical_url, external_posting_id="EX-999"))
    with pytest.raises(PostingIdentityConflictError):
        resolver.resolve(PostingIdentityInput(source, first.canonical_url, external_posting_id="EX-999", correlated_posting_id=second.id))
    with client.app.state.database.session_factory() as session:
        current = session.get(PostingModel, first.id)
        assert (current.stable_key, current.canonical_url) == before
        assert session.scalar(select(func.count()).select_from(PostingModel)) == 2


def test_duplicate_case_canonicalization_validation_and_decision_history(client) -> None:
    assert canonical_subject_pair("opportunity", "B", "A") == ("A", "B")
    with pytest.raises(ValueError):
        canonical_subject_pair("opportunity", "A", "A")
    first = valid_bundle()
    report = import_bundle(client, first).json()
    import_id = report["import_id"]
    with client.app.state.database.session_factory() as session:
        opportunity = session.scalar(select(OpportunityModel))
        reference = session.scalar(select(SourceReferenceModel))
        assessment_before = session.scalar(select(PersonalAssessmentModel))
    assessment = client.app.state.personal_triage_service.create_assessment(opportunity.id, "junior_suitability", 4, None)
    client.app.state.personal_triage_service.change_status(opportunity.id, "shortlisted")
    service = client.app.state.duplicate_case_service
    with client.app.state.database.session_factory.begin() as session:
        other_reference = SourceReferenceModel(
            id="manual-reference",
            import_id=import_id,
            bundle_local_id="manual-reference",
            source_id=reference.source_id,
            url="https://example.com/manual",
            normalized_url="https://example.com/manual",
            observed_at=reference.observed_at,
        )
        session.add(other_reference)
        session.flush()
        other_opportunity = OpportunityModel(
            id="manual-opportunity",
            import_id=import_id,
            bundle_local_id="manual-opportunity",
            company_id=opportunity.company_id,
            canonical_title="Manual role",
            source_reference_id=other_reference.id,
            observed_at=opportunity.observed_at,
        )
        session.add(other_opportunity)
    case = service.create(
        research_import_id=import_id,
        subject_type="opportunity",
        left_subject_id=opportunity.id,
        right_subject_id="manual-opportunity",
        evidence_summary="Potential duplicate",
        confidence=0.8,
        source_reference_ids=[reference.id],
    )
    reversed_case = service.create(
        research_import_id=import_id,
        subject_type="opportunity",
        left_subject_id="manual-opportunity",
        right_subject_id=opportunity.id,
        evidence_summary="Changed evidence must not overwrite",
        confidence=0.1,
        source_reference_ids=[reference.id],
    )
    assert reversed_case == case
    assert service.get(case.id) == case
    assert len(service.list(subject_type="opportunity", subject_id=opportunity.id)) == 1

    decided = service.decide(case.id, outcome="confirmed_duplicate", reason="Same role and evidence.")
    assert decided.is_reviewed
    assert decided.is_resolved
    assert decided.current_decision is not None
    assert decided.current_decision.sequence == 1
    assert decided.current_decision.outcome == "confirmed_duplicate"
    assert decided.current_decision.reason == "Same role and evidence."

    corrected = service.decide(case.id, outcome="keep_unresolved", reason="Need stronger identity evidence.")
    assert corrected.is_reviewed
    assert not corrected.is_resolved
    assert [decision.sequence for decision in corrected.decisions] == [1, 2]
    assert [decision.outcome for decision in corrected.decisions] == ["confirmed_duplicate", "keep_unresolved"]

    with pytest.raises(DuplicateDecisionConflictError):
        service.decide(case.id, outcome="keep_unresolved", reason="Repeated current outcome.")
    with pytest.raises(ValueError):
        service.decide(case.id, outcome="invalid", reason="Invalid outcome.")
    with pytest.raises(ValueError):
        service.decide(case.id, outcome="confirmed_distinct", reason="   ")

    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(DuplicateCaseModel)) == 1
        assert session.scalar(select(func.count()).select_from(DuplicateCaseDecisionModel)) == 2
        assert session.get(PersonalAssessmentModel, assessment["id"]).value_json == "4"
        assert session.get(OpportunityModel, opportunity.id).tracking_status == "shortlisted"
        assert assessment_before is None


def test_duplicate_case_posting_and_references_are_validated(client) -> None:
    postings = imported_postings(client)
    with client.app.state.database.session_factory() as session:
        import_id = session.get(PostingModel, postings[0].id).import_id
        reference = session.get(SourceReferenceModel, postings[0].source_reference_id)
    service = client.app.state.duplicate_case_service
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="posting",
            left_subject_id=postings[0].id,
            right_subject_id=postings[1].id,
            evidence_summary="x",
            confidence=0.5,
            source_reference_ids=["missing-reference"],
        )
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="posting",
            left_subject_id="missing-posting",
            right_subject_id=postings[0].id,
            evidence_summary="x",
            confidence=0.5,
            source_reference_ids=[reference.id],
        )
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="posting",
            left_subject_id=postings[0].id,
            right_subject_id="missing-posting-2",
            evidence_summary="   ",
            confidence=0.5,
            source_reference_ids=[reference.id],
        )
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="posting",
            left_subject_id=postings[0].id,
            right_subject_id="missing-posting-3",
            evidence_summary="x",
            confidence=1.1,
            source_reference_ids=[reference.id],
        )
    case = service.create(
        research_import_id=import_id,
        subject_type="posting",
        left_subject_id=postings[1].id,
        right_subject_id=postings[0].id,
        evidence_summary="Same role evidence",
        confidence=None,
        source_reference_ids=[reference.id],
    )
    assert case.left_subject_id < case.right_subject_id
    assert service.list(subject_type="posting") == [case]
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="company",
            left_subject_id=postings[0].id,
            right_subject_id=postings[1].id,
            evidence_summary="x",
            confidence=0.5,
            source_reference_ids=[reference.id],
        )
    with pytest.raises(ValueError):
        service.create(
            research_import_id=import_id,
            subject_type="posting",
            left_subject_id=postings[0].id,
            right_subject_id=postings[1].id,
            evidence_summary="x",
            confidence=0.5,
            source_reference_ids=[],
        )
