from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from sqlalchemy import func, select
from tests.test_imports import import_bundle, valid_bundle
from vocation.domain.availability import AvailabilityCheckResult, AvailabilityEvaluator, AvailabilityObservation
from vocation.infrastructure.models import (
    AvailabilityObservationModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptContextSubjectModel,
)


def observation(identifier: str, result: str, *, observed_at: datetime, recorded_at: datetime | None = None) -> AvailabilityObservation:
    return AvailabilityObservation(
        identifier,
        "posting-1",
        cast(AvailabilityCheckResult, result),
        observed_at,
        recorded_at or observed_at,
        "checked evidence",
    )


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ("explicitly_available", "available"),
        ("explicitly_unavailable", "unavailable"),
        ("temporarily_unreachable", "uncertain"),
        ("not_found", "uncertain"),
        ("indeterminate", "uncertain"),
    ],
)
def test_availability_evaluator_maps_exact_results(result: str, expected: str) -> None:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    assert AvailabilityEvaluator().posting((observation("a", result, observed_at=now),), now).availability == expected


def test_availability_evaluator_latest_ordering_and_age() -> None:
    now = datetime(2026, 8, 10, 12, tzinfo=UTC)
    old = observation("old", "explicitly_available", observed_at=now - timedelta(days=4))
    newer = observation("new", "explicitly_unavailable", observed_at=now - timedelta(days=2, hours=1))
    same_time_late_record = observation("z", "explicitly_available", observed_at=newer.observed_at, recorded_at=now)
    result = AvailabilityEvaluator().posting((old, newer, same_time_late_record), now)
    assert result.availability == "available"
    assert result.last_checked_at == newer.observed_at
    assert result.age_days == 2
    assert AvailabilityEvaluator().posting((), now).availability == "unknown"
    assert AvailabilityEvaluator().posting((), now).age_days is None


def test_availability_evaluator_opportunity_precedence_and_freshness() -> None:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    evaluator = AvailabilityEvaluator()
    available = (observation("a", "explicitly_available", observed_at=now - timedelta(days=1)),)
    uncertain = (observation("b", "not_found", observed_at=now - timedelta(days=3)),)
    unavailable = (observation("c", "explicitly_unavailable", observed_at=now - timedelta(days=2)),)
    assert evaluator.opportunity((unavailable, uncertain, available), now).availability == "available"
    assert evaluator.opportunity((unavailable, uncertain), now).availability == "uncertain"
    assert evaluator.opportunity((unavailable,), now).availability == "unavailable"
    assert evaluator.opportunity((), now).availability == "unknown"
    assert evaluator.opportunity((unavailable, uncertain), now).age_days == 2


def _availability_bundle(posting_ref: str = "posting-ref") -> dict:
    return {
        "bundle_kind": "availability_check",
        "bundle_version": "1.0",
        "bundle_id": "availability-1",
        "generated_at": "2026-08-10T12:00:00Z",
        "prompt_context_ref": "availability-context",
        "research_scope": {"type": "availability_check", "as_of_date": "2026-08-10", "selected_correlation_refs": [posting_ref]},
        "observations": [
            {
                "id": "availability-observation-1",
                "posting_correlation_ref": posting_ref,
                "result": "explicitly_available",
                "observed_at": "2026-08-10T11:00:00Z",
                "evidence_summary": "The posting is available.",
            }
        ],
        "warnings": [],
    }


def _prepare_context(client, *, target: bool = True) -> str:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory() as session:
        posting = session.scalar(select(PostingModel))
        snapshot = PromptContextSnapshotModel(
            prompt_context_ref="availability-context",
            scope_type="availability_check",
            as_of_date="2026-08-10",
            scope_json=json.dumps(_availability_bundle()["research_scope"]),
            fingerprint="a" * 64,
        )
        snapshot.subjects.append(
            PromptContextSubjectModel(
                prompt_context_ref="availability-context",
                correlation_ref="posting-ref",
                subject_type="posting",
                subject_id=posting.id,
                is_target=target,
            )
        )
        session.add(snapshot)
        session.commit()
        return posting.id


def _import_availability(client, bundle: dict | None = None):
    service = client.app.state.availability_import_service
    return service.import_text(json.dumps(bundle or _availability_bundle()))


def test_valid_availability_import_is_append_only_and_idempotent(client) -> None:
    posting_id = _prepare_context(client)
    first = _import_availability(client)
    assert first.status == "applied"
    assert first.import_kind == "availability_check"
    assert first.counts == {"availability_observations_created": 1}
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 1
        assert session.get(PostingModel, posting_id).id == posting_id
    duplicate = _import_availability(client)
    assert duplicate.status == "duplicate"
    assert duplicate.duplicate_of_import_id == first.import_id
    later = copy.deepcopy(_availability_bundle())
    later["bundle_id"] = "availability-2"
    later["observations"][0]["id"] = "availability-observation-2"
    later["observations"][0]["observed_at"] = "2026-08-10T11:30:00Z"
    second = _import_availability(client, later)
    assert second.status == "applied"
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 2


def test_availability_planning_blockers_happen_before_observation_write(client) -> None:
    _prepare_context(client, target=False)
    bundle = _availability_bundle()
    report = _import_availability(client, bundle)
    assert report.status == "rejected"
    assert {issue.code for issue in report.issues} == {"SCOPE_VIOLATION"}
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 0


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda bundle: bundle.update({"prompt_context_ref": "missing"}), "UNKNOWN_PROMPT_CONTEXT"),
        (lambda bundle: bundle["research_scope"].update({"as_of_date": "2026-08-09"}), "SCOPE_MISMATCH"),
        (
            lambda bundle: bundle["observations"].__setitem__(0, {**bundle["observations"][0], "observed_at": "2026-08-11T00:00:00Z"}),
            "INVALID_DATE",
        ),
    ],
)
def test_availability_import_reports_semantic_blockers(client, mutation, code: str) -> None:
    _prepare_context(client)
    bundle = _availability_bundle()
    mutation(bundle)
    report = _import_availability(client, bundle)
    assert report.status == "rejected"
    assert code in {issue.code for issue in report.issues}
