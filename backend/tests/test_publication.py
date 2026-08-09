from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import vocation
from jsonschema import Draft202012Validator, FormatChecker
from tests.test_imports import import_bundle, valid_bundle
from vocation.application.publication import (
    OpportunityOverviewPublicationService,
    PublicationOpportunitySource,
    PublicationWorkLocation,
)

ROOT = Path(__file__).resolve().parents[2]


class FakePublicationRepository:
    def __init__(self, opportunities: tuple[PublicationOpportunitySource, ...]) -> None:
        self.opportunities = opportunities

    def load_opportunities(self) -> tuple[PublicationOpportunitySource, ...]:
        return self.opportunities


def source(
    opportunity_ref: str,
    title: str,
    company_ref: str,
    company_name: str,
    locations: tuple[PublicationWorkLocation, ...] = (),
    posting_count: int = 0,
) -> PublicationOpportunitySource:
    return PublicationOpportunitySource(opportunity_ref, title, company_ref, company_name, locations, posting_count)


def test_publication_projection_is_typed_deterministic_and_opaque() -> None:
    repository = FakePublicationRepository(
        (
            source(
                "opp-b",
                "alpha",
                "company-b",
                "zeta",
                (
                    PublicationWorkLocation("Office", None, "North", None, "region"),
                    PublicationWorkLocation("Office", "Berlin", None, "DE", "city"),
                    PublicationWorkLocation("Home", None, None, None, "unknown"),
                ),
                4,
            ),
            source("opp-a", "Beta", "company-a", "alpha", posting_count=1),
        )
    )
    service = OpportunityOverviewPublicationService(
        repository,
        ref_factory=lambda: "publication-ref",
        clock=lambda: datetime(2026, 8, 9, 10, 11, 12, tzinfo=UTC),
    )

    artifact = service.generate().as_dict()

    assert artifact["capability"] == "vocation.opportunity_overview"
    assert artifact["contract_version"] == "1.0"
    assert artifact["publication"] == {
        "publication_ref": "publication-ref",
        "generated_at": "2026-08-09T10:11:12Z",
    }
    assert [item["opportunity_ref"] for item in artifact["opportunities"]] == ["opp-a", "opp-b"]
    assert [item["label"] for item in artifact["opportunities"][1]["work_locations"]] == [
        "Home",
        "Office",
        "Office",
    ]
    assert artifact["opportunities"][1]["work_locations"][2]["city"] is None
    assert artifact["opportunities"][1]["posting_count"] == 4


def test_empty_market_and_repeated_generation_keep_opportunities_identical() -> None:
    empty = OpportunityOverviewPublicationService(FakePublicationRepository(()), ref_factory=lambda: "r")
    assert empty.generate().as_dict()["opportunities"] == []

    repository = FakePublicationRepository((source("opp", "Role", "company", "Company"),))
    refs = iter(("r1", "r2"))
    times = iter(
        (
            datetime(2026, 8, 9, tzinfo=UTC),
            datetime(2026, 8, 10, tzinfo=UTC),
        )
    )
    service = OpportunityOverviewPublicationService(repository, ref_factory=lambda: next(refs), clock=lambda: next(times))
    first = service.generate().as_dict()
    second = service.generate().as_dict()
    assert first["opportunities"] == second["opportunities"]
    assert first["publication"] != second["publication"]


def test_published_endpoint_validates_and_isolated_from_internal_state(client) -> None:
    response = client.get("/published/v1/opportunity-overview")
    assert response.status_code == 200
    artifact = response.json()
    schema = json.loads((ROOT / "schemas" / "published-opportunity-overview-v1.schema.json").read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(artifact))
    assert "/published/v1/opportunity-overview" not in client.app.openapi()["paths"]

    forbidden = {
        "tracking_status",
        "personal_assessments",
        "decisions",
        "excluded",
        "restore",
        "external_assessments",
        "observations",
        "import_id",
        "imported_at",
        "bundle_id",
        "fingerprint",
        "prompt_context_ref",
        "duplicate_cases",
        "url",
        "availability",
        "freshness",
        "coordinates",
    }

    def keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    assert not forbidden.intersection(keys(artifact))
    assert vocation.__version__ == "0.3.0"
    assert client.app.version == vocation.__version__


def test_seeded_market_projects_without_personal_fields(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    response = client.get("/published/v1/opportunity-overview")
    assert response.status_code == 200
    opportunity = response.json()["opportunities"][0]
    assert opportunity["title"] == "Junior Softwareentwickler"
    assert opportunity["company"]["name"] == "Example GmbH"
    assert opportunity["posting_count"] == 1


def test_personal_state_does_not_change_public_projection(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    before = client.get("/published/v1/opportunity-overview").json()["opportunities"]
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    assessment = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "private-note"},
    )
    assert assessment.status_code == 201
    status = client.post(f"/api/opportunities/{opportunity_id}/status", json={"status": "shortlisted"})
    assert status.status_code == 200
    after = client.get("/published/v1/opportunity-overview").json()["opportunities"]
    assert after == before
