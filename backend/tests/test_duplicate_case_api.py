from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import func, select
from vocation.infrastructure.models import OpportunityModel, PostingModel, SourceReferenceModel

ROOT = Path(__file__).resolve().parents[2]


def valid_bundle() -> dict:
    return json.loads((ROOT / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8"))


def seed_duplicate_cases(client) -> dict[str, str]:
    response = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle(), ensure_ascii=False)})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    import_id = response.json()["import_id"]

    with client.app.state.database.session_factory() as session:
        opportunity = session.scalar(select(OpportunityModel))
        posting = session.scalar(select(PostingModel))
        reference = session.scalar(select(SourceReferenceModel))
        assert opportunity is not None
        assert posting is not None
        assert reference is not None
        opportunity_id = opportunity.id
        posting_id = posting.id
        company_id = opportunity.company_id
        source_id = reference.source_id
        observed_at = reference.observed_at

    client.app.state.personal_triage_service.change_status(opportunity_id, "shortlisted")

    with client.app.state.database.session_factory.begin() as session:
        second_reference = SourceReferenceModel(
            id="duplicate-api-ref-2",
            import_id=import_id,
            bundle_local_id="duplicate-api-ref-2",
            source_id=source_id,
            url="https://example.com/careers/duplicate-api-two",
            normalized_url="https://example.com/careers/duplicate-api-two",
            observed_at=observed_at,
        )
        session.add(second_reference)
        session.flush()
        second_opportunity = OpportunityModel(
            id="duplicate-api-opportunity-2",
            import_id=import_id,
            bundle_local_id="duplicate-api-opportunity-2",
            company_id=company_id,
            canonical_title="Junior Software Engineer Alternative",
            source_reference_id=second_reference.id,
            observed_at=observed_at,
        )
        session.add(second_opportunity)
        second_posting = PostingModel(
            id="duplicate-api-posting-2",
            import_id=import_id,
            bundle_local_id="duplicate-api-posting-2",
            company_id=company_id,
            opportunity_id=second_opportunity.id,
            source_reference_id=second_reference.id,
            title="Junior Software Engineer Alternative Posting",
            external_posting_id="DUP-API-2",
            stable_key="external:duplicate-api:2",
            canonical_url=second_reference.normalized_url,
            published_at=None,
            observed_at=observed_at,
            content_fingerprint=None,
        )
        session.add(second_posting)

    service = client.app.state.duplicate_case_service
    opportunity_case = service.create(
        research_import_id=import_id,
        subject_type="opportunity",
        left_subject_id=opportunity_id,
        right_subject_id="duplicate-api-opportunity-2",
        evidence_summary="The opportunity titles and employer overlap.",
        confidence=0.8,
        source_reference_ids=[reference.id],
    )
    posting_case = service.create(
        research_import_id=import_id,
        subject_type="posting",
        left_subject_id=posting_id,
        right_subject_id="duplicate-api-posting-2",
        evidence_summary="The postings may describe the same opening.",
        confidence=0.6,
        source_reference_ids=[reference.id, "duplicate-api-ref-2"],
    )
    return {
        "opportunity_id": opportunity_id,
        "posting_id": posting_id,
        "opportunity_case_id": opportunity_case.id,
        "posting_case_id": posting_case.id,
    }


def test_duplicate_case_review_api_lists_both_subject_types_with_context(client) -> None:
    seeded = seed_duplicate_cases(client)

    response = client.get("/api/duplicate-cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 2

    opportunity_case = next(item for item in cases if item["subject_type"] == "opportunity")
    assert opportunity_case["id"] == seeded["opportunity_case_id"]
    assert opportunity_case["left_subject"]["subject_type"] == "opportunity"
    assert opportunity_case["left_subject"]["title"]
    assert opportunity_case["left_subject"]["context"]
    assert opportunity_case["right_subject"]["title"] == "Junior Software Engineer Alternative"
    assert opportunity_case["source_references"][0]["source_name"]
    assert opportunity_case["source_references"][0]["url"].startswith("https://")
    assert opportunity_case["current_decision"] is None
    assert opportunity_case["decision_history"] == []
    assert opportunity_case["is_reviewed"] is False
    assert opportunity_case["is_resolved"] is False

    posting_case = next(item for item in cases if item["subject_type"] == "posting")
    assert posting_case["id"] == seeded["posting_case_id"]
    assert posting_case["left_subject"]["subject_type"] == "posting"
    assert posting_case["left_subject"]["title"]
    assert posting_case["left_subject"]["context"]
    assert posting_case["right_subject"]["title"] == "Junior Software Engineer Alternative Posting"
    assert len(posting_case["source_references"]) == 2

    filtered = client.get(
        "/api/duplicate-cases",
        params={"subject_type": "opportunity", "subject_id": seeded["opportunity_id"]},
    )
    assert filtered.status_code == 200
    assert [item["id"] for item in filtered.json()] == [seeded["opportunity_case_id"]]

    detail = client.get(f"/api/duplicate-cases/{seeded['posting_case_id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == seeded["posting_case_id"]
    assert client.get("/api/duplicate-cases/missing-case").status_code == 404


def test_duplicate_case_decision_api_appends_history_without_merging_subjects(client) -> None:
    seeded = seed_duplicate_cases(client)
    case_id = seeded["opportunity_case_id"]

    first = client.post(
        f"/api/duplicate-cases/{case_id}/decisions",
        json={"outcome": "confirmed_duplicate", "reason": "  Same underlying role.  "},
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["current_decision"]["sequence"] == 1
    assert first_body["current_decision"]["outcome"] == "confirmed_duplicate"
    assert first_body["current_decision"]["reason"] == "Same underlying role."
    assert first_body["is_reviewed"] is True
    assert first_body["is_resolved"] is True
    assert len(first_body["decision_history"]) == 1

    corrected = client.post(
        f"/api/duplicate-cases/{case_id}/decisions",
        json={"outcome": "keep_unresolved", "reason": "Need stronger evidence before any future merge."},
    )
    assert corrected.status_code == 200
    corrected_body = corrected.json()
    assert corrected_body["current_decision"]["sequence"] == 2
    assert corrected_body["current_decision"]["outcome"] == "keep_unresolved"
    assert corrected_body["is_reviewed"] is True
    assert corrected_body["is_resolved"] is False
    assert [item["outcome"] for item in corrected_body["decision_history"]] == [
        "confirmed_duplicate",
        "keep_unresolved",
    ]

    repeated = client.post(
        f"/api/duplicate-cases/{case_id}/decisions",
        json={"outcome": "keep_unresolved", "reason": "Repeated."},
    )
    assert repeated.status_code == 409
    assert client.post(
        f"/api/duplicate-cases/{case_id}/decisions",
        json={"outcome": "confirmed_distinct", "reason": "   "},
    ).status_code == 422
    assert client.post(
        "/api/duplicate-cases/missing-case/decisions",
        json={"outcome": "confirmed_distinct", "reason": "Different roles."},
    ).status_code == 404

    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(OpportunityModel)) == 2
        assert session.scalar(select(func.count()).select_from(PostingModel)) == 2
        assert session.get(OpportunityModel, seeded["opportunity_id"]).tracking_status == "shortlisted"
        assert session.get(OpportunityModel, "duplicate-api-opportunity-2") is not None
        assert session.get(PostingModel, seeded["posting_id"]) is not None
        assert session.get(PostingModel, "duplicate-api-posting-2") is not None
