from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from tests.test_imports import valid_bundle
from vocation.application.comparison import (
    ComparisonCriterion,
    ComparisonExternalAssessment,
    ComparisonObservation,
    ComparisonOpportunity,
    ComparisonPersonalAssessment,
    ComparisonWorkLocation,
    OpportunityComparisonService,
)
from vocation.domain.availability import AvailabilityObservation


class FakeComparisonRepository:
    def __init__(self, records):
        self.records = {record.opportunity_id: record for record in records}

    def get_many(self, opportunity_ids):
        return [self.records[opportunity_id] for opportunity_id in opportunity_ids if opportunity_id in self.records]

    def criteria(self, criterion_ids):
        return [ComparisonCriterion(criterion_id, criterion_id.upper(), index) for index, criterion_id in enumerate(sorted(criterion_ids))]


def record(opportunity_id: str, *, company_id: str = "company") -> ComparisonOpportunity:
    now = datetime(2026, 8, 10, 12, tzinfo=UTC)
    posting_id = f"posting-{opportunity_id}"
    return ComparisonOpportunity(
        opportunity_id=opportunity_id,
        title=f"Title {opportunity_id}",
        company_id=company_id,
        company_name="Company",
        work_locations=(ComparisonWorkLocation("Hamburg", "city"),),
        tracking_status="new",
        groups=(),
        postings=(posting_id,),
        observations=(
            ComparisonObservation("company-observation", "opportunity", opportunity_id, "task", ["build"], now, "opportunity"),
            ComparisonObservation("posting-observation", "posting", posting_id, "task", ["build"], now - timedelta(hours=1), "posting"),
            ComparisonObservation("posting-observation-2", "posting", posting_id, "task", ["test"], now, "newer"),
        ),
        availability_observations=((AvailabilityObservation("availability", posting_id, "explicitly_available", now, now, "checked"),),),
        personal_assessments=(ComparisonPersonalAssessment("criterion", 4, "current", now),),
        external_assessments=(ComparisonExternalAssessment("external", "criterion", 5, "external", now),),
    )


def test_comparison_preserves_order_and_reduces_distinct_evidence() -> None:
    service = OpportunityComparisonService(
        FakeComparisonRepository([record("a"), record("b")]),
        clock=lambda: datetime(2026, 8, 11, tzinfo=UTC),
    )

    comparison = service.compare(["b", "a"])

    assert [item.opportunity_id for item in comparison.opportunities] == ["b", "a"]
    cell = comparison.opportunities[0].research_dimensions["task"]
    assert cell.state == "present"
    assert [item.value for item in cell.values] == [["test"], ["build"]]
    assert all(item.subject_type != "company" for item in cell.values)
    assert comparison.opportunities[0].availability == "available"
    assert comparison.assessment_criteria[0].criterion_id == "criterion"


def test_comparison_rejects_invalid_selection_and_missing_opportunity() -> None:
    service = OpportunityComparisonService(FakeComparisonRepository([record("a"), record("b")]))

    with pytest.raises(ValueError):
        service.compare(["a"])
    with pytest.raises(ValueError):
        service.compare(["a", "a"])
    with pytest.raises(LookupError):
        service.compare(["a", "missing"])


def test_comparison_http_returns_requested_order(client) -> None:
    first = valid_bundle()
    second = deepcopy(first)
    second_json = json.dumps(second).replace("example", "second")
    second = json.loads(second_json)
    assert client.post("/api/imports/text", json={"content": json.dumps(first)}).json()["status"] == "applied"
    assert client.post("/api/imports/text", json={"content": json.dumps(second)}).json()["status"] == "applied"
    opportunities = client.get("/api/opportunities").json()
    ids = [item["id"] for item in opportunities]

    response = client.post("/api/comparison/opportunities", json={"opportunity_ids": ids[::-1]})

    assert response.status_code == 200
    assert [item["opportunity_id"] for item in response.json()["opportunities"]] == ids[::-1]
    assert response.json()["opportunities"][0]["research_dimensions"]["task"]["state"] == "missing"
