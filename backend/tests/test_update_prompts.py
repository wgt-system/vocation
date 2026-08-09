from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from vocation.infrastructure.models import (
    CompanyModel,
    DuplicateCaseModel,
    DuplicateCaseSourceReferenceModel,
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptRunModel,
    ResearchImportModel,
    SourceReferenceModel,
)


def _initial_bundle() -> str:
    return (Path(__file__).resolve().parents[2] / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8")


def _context(prompt_text: str) -> dict:
    body = prompt_text.split("## Prompt Context\n", 1)[1].split("\n\n## Active Assessment Criteria", 1)[0]
    return json.loads(body)


def _market_ids(app) -> tuple[str, str, str]:
    with app.state.database.session_factory() as session:
        company = session.query(CompanyModel).one()
        opportunity = session.query(OpportunityModel).one()
        posting = session.query(PostingModel).one()
        return company.id, opportunity.id, posting.id


def _import_second_graph(client) -> None:
    bundle = json.loads(_initial_bundle())
    replacements = {
        "example-initial-001": "example-initial-002",
        "src-company": "src-second",
        "ref-posting": "ref-second",
        "cmp-example": "cmp-second",
        "opp-example": "opp-second",
        "post-example": "post-second",
        "obs-tech": "obs-second",
        "ass-junior": "ass-second",
        "https://example.com/careers": "https://other.example/careers",
        "https://example.com/careers/junior-dev": "https://other.example/careers/second-dev",
        "EX-123": "EX-456",
    }

    def replace(value):
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, str):
            return replacements.get(value, value)
        return value

    bundle = replace(bundle)
    response = client.post("/api/imports/text", json={"content": json.dumps(bundle)})
    assert response.json()["status"] == "applied", response.json()["issues"]


def _ids_by_import(app) -> dict[str, dict[str, str]]:
    with app.state.database.session_factory() as session:
        companies = session.scalars(select(CompanyModel).order_by(CompanyModel.id)).all()
        opportunities = session.scalars(select(OpportunityModel).order_by(OpportunityModel.id)).all()
        postings = session.scalars(select(PostingModel).order_by(PostingModel.id)).all()
        result = {
            "first": {
                "company": next(item.id for item in companies if item.canonical_name == "Example GmbH"),
                "opportunity": next(item.id for item in opportunities if item.canonical_title == "Junior Softwareentwickler"),
                "posting": next(item.id for item in postings if item.title == "Junior Softwareentwickler"),
            },
        }
        if len(companies) > 1:
            result["second"] = {
                "company": next(item.id for item in companies if item.import_id != companies[0].import_id),
                "opportunity": next(item.id for item in opportunities if item.import_id != opportunities[0].import_id),
                "posting": next(item.id for item in postings if item.import_id != postings[0].import_id),
            }
        return result


def _persisted_scope(app, prompt_context_ref: str) -> dict:
    with app.state.database.session_factory() as session:
        snapshot = session.get(PromptContextSnapshotModel, prompt_context_ref)
        assert snapshot is not None
        return json.loads(snapshot.scope_json)


def _seed_duplicate_case(app, ids: dict[str, dict[str, str]]) -> None:
    with app.state.database.session_factory.begin() as session:
        import_id = session.scalar(select(ResearchImportModel.id).order_by(ResearchImportModel.created_at))
        reference_id = session.scalar(select(SourceReferenceModel.id).order_by(SourceReferenceModel.id))
        assert import_id is not None
        assert reference_id is not None
        case_id = str(uuid4())
        session.add(
            DuplicateCaseModel(
                id=case_id,
                research_import_id=import_id,
                subject_type="opportunity",
                left_subject_id=min(ids["first"]["opportunity"], ids["second"]["opportunity"]),
                right_subject_id=max(ids["first"]["opportunity"], ids["second"]["opportunity"]),
                evidence_summary="Possible same opportunity",
                confidence=0.7,
                created_at=datetime(2026, 8, 8, tzinfo=UTC),
            )
        )
        session.add(DuplicateCaseSourceReferenceModel(duplicate_case_id=case_id, source_reference_id=reference_id))


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

    company_result = app.state.prompt_service.generate_update(mode="company_update", as_of_date="2026-08-09", selected_ids=[company_id])
    company_context = _context(company_result.prompt_text)
    assert company_context["research_scope"]["selected_correlation_refs"] == [
        company_context["known_subjects"]["companies"][0]["correlation_ref"]
    ]
    assert _persisted_scope(app, company_result.prompt_context_ref) == company_context["research_scope"]
    assert all(item["is_target"] for group in company_context["known_subjects"].values() for item in group)

    opportunity_result = app.state.prompt_service.generate_update(
        mode="opportunity_update", as_of_date="2026-08-09", selected_ids=[opportunity_id]
    )
    opportunity_context = _context(opportunity_result.prompt_text)
    assert opportunity_context["known_subjects"]["companies"][0]["is_target"] is False
    assert opportunity_context["known_subjects"]["opportunities"][0]["is_target"] is True
    assert opportunity_context["known_subjects"]["postings"][0]["is_target"] is True
    assert _persisted_scope(app, opportunity_result.prompt_context_ref) == opportunity_context["research_scope"]

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
    assert all(item["is_target"] for name, group in gap_context["known_subjects"].items() if name != "companies" for item in group)
    assert {item["type"] for item in gap_context["latest_observations"]} == {"technology_requirement"}
    assert {item["criterion_id"] for item in gap_context["latest_external_assessments"]} == {"junior_suitability"}
    assert gap_context["unresolved_duplicate_cases"] == []
    assert _persisted_scope(app, gap_result.prompt_context_ref) == gap_context["research_scope"]


def test_company_and_opportunity_scopes_exclude_unrelated_subjects(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    _import_second_graph(client)
    ids = _ids_by_import(app)

    company_context = _context(
        app.state.prompt_service.generate_update(
            mode="company_update", as_of_date="2026-08-09", selected_ids=[ids["first"]["company"]]
        ).prompt_text
    )
    assert len(company_context["known_subjects"]["companies"]) == 1
    assert len(company_context["known_subjects"]["opportunities"]) == 1
    assert len(company_context["known_subjects"]["postings"]) == 1

    opportunity_context = _context(
        app.state.prompt_service.generate_update(
            mode="opportunity_update", as_of_date="2026-08-09", selected_ids=[ids["first"]["opportunity"]]
        ).prompt_text
    )
    assert len(opportunity_context["known_subjects"]["companies"]) == 1
    assert len(opportunity_context["known_subjects"]["opportunities"]) == 1
    assert len(opportunity_context["known_subjects"]["postings"]) == 1
    assert opportunity_context["known_subjects"]["companies"][0]["is_target"] is False


def test_latest_evidence_is_reduced_per_subject_and_field(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    ids = _ids_by_import(app)["first"]
    with app.state.database.session_factory.begin() as session:
        import_id = session.scalar(select(ResearchImportModel.id).order_by(ResearchImportModel.created_at))
        reference_id = session.scalar(select(SourceReferenceModel.id).order_by(SourceReferenceModel.id))
        assert import_id is not None and reference_id is not None
        session.add_all(
            [
                ObservationModel(
                    id=str(uuid4()),
                    import_id=import_id,
                    bundle_local_id="old-task",
                    subject_type="posting",
                    subject_id=ids["posting"],
                    observation_type="task",
                    value_json=json.dumps("old"),
                    source_reference_id=reference_id,
                    observed_at=datetime(2026, 8, 1, tzinfo=UTC),
                    confidence=0.4,
                    evidence_summary="old evidence",
                ),
                ObservationModel(
                    id=str(uuid4()),
                    import_id=import_id,
                    bundle_local_id="new-task",
                    subject_type="posting",
                    subject_id=ids["posting"],
                    observation_type="task",
                    value_json=json.dumps("new"),
                    source_reference_id=reference_id,
                    observed_at=datetime(2026, 8, 9, tzinfo=UTC),
                    confidence=0.9,
                    evidence_summary="new evidence",
                ),
                ExternalAssessmentModel(
                    id=str(uuid4()),
                    import_id=import_id,
                    bundle_local_id="old-assessment",
                    subject_type="opportunity",
                    subject_id=ids["opportunity"],
                    criterion_id="junior_suitability",
                    value_json="2",
                    origin="external_research",
                    source_reference_ids_json=json.dumps([reference_id]),
                    created_at=datetime(2026, 8, 1, tzinfo=UTC),
                    reasoning="old assessment",
                ),
                ExternalAssessmentModel(
                    id=str(uuid4()),
                    import_id=import_id,
                    bundle_local_id="new-assessment",
                    subject_type="opportunity",
                    subject_id=ids["opportunity"],
                    criterion_id="junior_suitability",
                    value_json="4",
                    origin="external_research",
                    source_reference_ids_json=json.dumps([reference_id]),
                    created_at=datetime(2026, 8, 9, tzinfo=UTC),
                    reasoning="new assessment",
                ),
            ]
        )

    context = _context(app.state.prompt_service.generate_update(mode="full_update", as_of_date="2026-08-09").prompt_text)
    tasks = [item for item in context["latest_observations"] if item["type"] == "task"]
    assessments = [item for item in context["latest_external_assessments"] if item["criterion_id"] == "junior_suitability"]
    assert [item["value"] for item in tasks] == ["new"]
    assert [item["value"] for item in assessments] == [4]
    assert "old evidence" not in json.dumps(context)
    assert "old assessment" not in json.dumps(context)


def test_duplicate_cases_follow_target_scope_and_are_absent_from_gap(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    _import_second_graph(client)
    ids = _ids_by_import(app)
    _seed_duplicate_case(app, ids)

    full_context = _context(app.state.prompt_service.generate_update(mode="full_update", as_of_date="2026-08-09").prompt_text)
    assert len(full_context["unresolved_duplicate_cases"]) == 1

    company_context = _context(
        app.state.prompt_service.generate_update(
            mode="company_update", as_of_date="2026-08-09", selected_ids=[ids["first"]["company"]]
        ).prompt_text
    )
    assert company_context["unresolved_duplicate_cases"] == []

    gap_context = _context(
        app.state.prompt_service.generate_update(
            mode="gap_filling",
            as_of_date="2026-08-09",
            gap_requests=[{"subject_type": "opportunity", "subject_id": ids["first"]["opportunity"], "criterion_id": "junior_suitability"}],
        ).prompt_text
    )
    assert gap_context["unresolved_duplicate_cases"] == []


def test_gap_minimizes_evidence_and_criteria_snapshot(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    ids = _ids_by_import(app)["first"]
    result = app.state.prompt_service.generate_update(
        mode="gap_filling",
        as_of_date="2026-08-09",
        gap_requests=[
            {"subject_type": "posting", "subject_id": ids["posting"], "observation_type": "technology_requirement"},
            {"subject_type": "opportunity", "subject_id": ids["opportunity"], "criterion_id": "junior_suitability"},
        ],
    )
    context = _context(result.prompt_text)
    criteria = json.loads(result.prompt_text.split("## Active Assessment Criteria\n", 1)[1].split("\n\n## Scope restrictions", 1)[0])
    assert {item["type"] for item in context["latest_observations"]} == {"technology_requirement"}
    assert {item["criterion_id"] for item in context["latest_external_assessments"]} == {"junior_suitability"}
    assert [item["criterion_id"] for item in criteria] == ["junior_suitability"]
    assert result.criteria_count == 1


def test_update_prompt_embeds_exact_output_schema_and_excludes_personal_state(client, app) -> None:
    assert client.post("/api/imports/text", json={"content": _initial_bundle()}).json()["status"] == "applied"
    opportunity_id = _market_ids(app)[1]
    personal = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "SECRET_PERSONAL_REASON"},
    )
    assert personal.status_code == 201
    assert client.post(f"/api/opportunities/{opportunity_id}/status", json={"status": "shortlisted"}).status_code == 200
    assert client.post(f"/api/opportunities/{opportunity_id}/exclude", json={"reason": "SECRET_DECISION_REASON"}).status_code == 200

    result = app.state.prompt_service.generate_update(mode="full_update", as_of_date="2026-08-09")
    schema = (Path(__file__).resolve().parents[2] / "schemas" / "research-update-bundle-v2.schema.json").read_text(encoding="utf-8")
    context = _context(result.prompt_text)
    assert schema in result.prompt_text
    assert "SECRET_PERSONAL_REASON" not in json.dumps(context)
    assert "SECRET_DECISION_REASON" not in json.dumps(context)
    assert "shortlisted" not in json.dumps(context)
    assert "excluded" not in json.dumps(context)
    assert result.prompt_text.count("bundle_version") >= 2
