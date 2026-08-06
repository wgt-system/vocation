from __future__ import annotations

import copy
import json
from pathlib import Path

from sqlalchemy import func, select

from vocation.infrastructure.models import (
    CompanyModel,
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    ResearchImportModel,
    SourceReferenceModel,
)


ROOT = Path(__file__).resolve().parents[2]


def valid_bundle() -> dict:
    return json.loads((ROOT / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8"))


def import_bundle(client, bundle: dict):
    return client.post("/api/imports/text", json={"content": json.dumps(bundle, ensure_ascii=False)})


def count_rows(client, model) -> int:
    with client.app.state.database.session_factory() as session:
        return session.scalar(select(func.count()).select_from(model))


def issue_codes(response) -> set[str]:
    return {issue["code"] for issue in response.json()["issues"]}


def test_valid_initial_bundle_imports_atomically_and_retains_provenance(client) -> None:
    response = import_bundle(client, valid_bundle())
    assert response.status_code == 200
    report = response.json()
    assert report["status"] == "applied"
    assert report["counts"]["opportunities"] == 1
    assert report["issues"] == []
    assert count_rows(client, CompanyModel) == 1
    assert count_rows(client, OpportunityModel) == 1
    assert count_rows(client, PostingModel) == 1

    with client.app.state.database.session_factory() as session:
        reference = session.scalar(select(SourceReferenceModel))
        observation = session.scalar(select(ObservationModel))
        assessment = session.scalar(select(ExternalAssessmentModel))
        assert reference.url == "https://example.com/careers/junior-dev"
        assert observation.source_reference_id == reference.id
        assert observation.evidence_summary == "Technologies listed in requirements"
        assert reference.id in json.loads(assessment.source_reference_ids_json)
        assert assessment.origin == "external_research"


def test_nested_unknown_property_is_rejected(client) -> None:
    content = (ROOT / "examples" / "imports" / "invalid-nested-property.json").read_text(encoding="utf-8")
    response = client.post("/api/imports/text", json={"content": content})
    assert response.json()["status"] == "rejected"
    assert "SCHEMA_VALIDATION_FAILED" in issue_codes(response)


def test_protected_personal_state_is_rejected(client) -> None:
    content = (ROOT / "examples" / "imports" / "invalid-protected-decision.json").read_text(encoding="utf-8")
    response = client.post("/api/imports/text", json={"content": content})
    assert response.json()["status"] == "rejected"
    assert issue_codes(response) == {"PROTECTED_FIELD_ATTEMPT"}


def test_unknown_assessment_criterion_rolls_back_entire_bundle(client) -> None:
    bundle = valid_bundle()
    bundle["assessments"][0]["criterion_id"] = "invented_by_research"
    response = import_bundle(client, bundle)
    assert response.json()["status"] == "rejected"
    assert "UNKNOWN_ASSESSMENT_CRITERION" in issue_codes(response)
    assert count_rows(client, CompanyModel) == 0
    assert count_rows(client, OpportunityModel) == 0
    assert count_rows(client, ResearchImportModel) == 1


def test_broken_reference_is_rejected(client) -> None:
    bundle = valid_bundle()
    bundle["postings"][0]["opportunity_id"] = "missing-opportunity"
    response = import_bundle(client, bundle)
    assert response.json()["status"] == "rejected"
    assert "UNKNOWN_REFERENCE" in issue_codes(response)


def test_duplicate_bundle_local_id_is_rejected(client) -> None:
    bundle = valid_bundle()
    bundle["sources"].append(copy.deepcopy(bundle["sources"][0]))
    response = import_bundle(client, bundle)
    assert response.json()["status"] == "rejected"
    assert "DUPLICATE_BUNDLE_ID" in issue_codes(response)


def test_unsafe_or_malformed_posting_url_is_rejected(client) -> None:
    for url in ("http://example.com/job", "javascript:alert(1)", "/relative/job"):
        bundle = valid_bundle()
        bundle["bundle_id"] = f"unsafe-{len(url)}"
        bundle["source_references"][0]["url"] = url
        response = import_bundle(client, bundle)
        assert response.json()["status"] == "rejected"
        assert "INVALID_URL" in issue_codes(response)
    assert count_rows(client, PostingModel) == 0


def test_reimport_and_object_key_order_are_idempotent(client) -> None:
    bundle = valid_bundle()
    first = client.post("/api/imports/text", json={"content": json.dumps(bundle, indent=2)})
    second = client.post("/api/imports/text", json={"content": json.dumps(bundle, sort_keys=True)})
    assert first.json()["status"] == "applied"
    assert second.json()["status"] == "duplicate"
    assert second.json()["duplicate_of_import_id"] == first.json()["import_id"]
    assert count_rows(client, OpportunityModel) == 1
    assert count_rows(client, ResearchImportModel) == 1


def test_file_import_and_report_lookup(client) -> None:
    content = (ROOT / "examples" / "imports" / "initial-valid.json").read_bytes()
    imported = client.post("/api/imports/file", files={"file": ("bundle.json", content, "application/json")})
    assert imported.status_code == 200
    report_id = imported.json()["import_id"]
    report = client.get(f"/api/imports/{report_id}")
    assert report.status_code == 200
    assert report.json()["status"] == "applied"


def test_opportunity_list_and_detail_contain_imported_data(client) -> None:
    imported = import_bundle(client, valid_bundle()).json()
    response = client.get("/api/opportunities")
    assert response.status_code == 200
    opportunities = response.json()
    assert len(opportunities) == 1
    assert opportunities[0]["title"] == "Junior Softwareentwickler"
    assert opportunities[0]["company_name"] == "Example GmbH"
    assert opportunities[0]["locations"] == ["Hamburg"]

    detail = client.get(f"/api/opportunities/{opportunities[0]['id']}")
    assert detail.status_code == 200
    value = detail.json()
    assert value["company"]["name"] == "Example GmbH"
    assert value["postings"][0]["source"]["name"] == "Example Careers"
    assert value["postings"][0]["source_reference"]["url"].startswith("https://")
    assert value["assessments"][0]["criterion_id"] == "junior_suitability"
    assert value["observations"][0]["evidence_summary"]
    assert value["import_provenance"]["import_id"] == imported["import_id"]
