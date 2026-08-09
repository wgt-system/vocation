from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from sqlalchemy import event, func, select
from tests.test_imports import import_bundle, valid_bundle
from vocation.application.availability_imports import AvailabilityImportPlanner
from vocation.domain.availability import AvailabilityCheckResult, AvailabilityEvaluator, AvailabilityObservation
from vocation.domain.update_import import ExistingSubject, PromptContextSnapshot, PromptContextSubject
from vocation.infrastructure.models import (
    AvailabilityObservationModel,
    CompanyModel,
    OpportunityModel,
    PostingModel,
    PromptContextSnapshotModel,
    PromptContextSubjectModel,
    ResearchImportModel,
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


@pytest.mark.parametrize(
    ("observed_delta", "expected_age"),
    [(timedelta(hours=23, minutes=59), 0), (timedelta(days=1), 1), (timedelta(days=1, hours=23, minutes=59), 1), (timedelta(days=2), 2)],
)
def test_availability_evaluator_floors_whole_elapsed_days(observed_delta: timedelta, expected_age: int) -> None:
    now = datetime(2026, 8, 10, 12, tzinfo=UTC)
    result = AvailabilityEvaluator().posting((observation("a", "explicitly_available", observed_at=now - observed_delta),), now)
    assert result.age_days == expected_age


def test_availability_evaluator_uses_internal_id_as_third_tie_breaker() -> None:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    observed_at = now - timedelta(days=1)
    recorded_at = now - timedelta(hours=1)
    observations = (
        observation("a", "explicitly_unavailable", observed_at=observed_at, recorded_at=recorded_at),
        observation("b", "explicitly_available", observed_at=observed_at, recorded_at=recorded_at),
    )
    assert AvailabilityEvaluator().posting(observations, now).availability == "available"


def test_availability_evaluator_future_timestamp_clamps_age_to_zero() -> None:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    result = AvailabilityEvaluator().posting((observation("a", "explicitly_available", observed_at=now + timedelta(days=2)),), now)
    assert result.age_days == 0


def test_availability_evaluator_unknown_aggregate_precedence_and_global_freshness() -> None:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    evaluator = AvailabilityEvaluator()
    unknown = ()
    unavailable = (observation("u", "explicitly_unavailable", observed_at=now - timedelta(days=5)),)
    uncertain = (observation("c", "not_found", observed_at=now - timedelta(days=3)),)
    available = (observation("a", "explicitly_available", observed_at=now - timedelta(days=1)),)
    assert evaluator.opportunity((unavailable, unknown), now).availability == "unknown"
    assert evaluator.opportunity((uncertain, unknown), now).availability == "uncertain"
    aggregate = evaluator.opportunity((available, uncertain, unknown), now)
    assert aggregate.availability == "available"
    assert aggregate.last_checked_at == available[0].observed_at


class FakeSnapshotRepository:
    def __init__(self, snapshot: PromptContextSnapshot | None):
        self.snapshot = snapshot

    def get(self, _ref: str):
        return self.snapshot


class FakeSubjectRepository:
    def __init__(self, subjects: set[str]):
        self.subjects = subjects

    def get(self, subject_type: str, subject_id: str):
        if subject_type == "posting" and subject_id in self.subjects:
            return ExistingSubject("posting", subject_id)
        return None


def _planner_bundle(refs: list[str], observations: list[dict]) -> dict:
    bundle = _availability_bundle(refs[0])
    bundle["research_scope"]["selected_correlation_refs"] = refs
    bundle["observations"] = observations
    return bundle


def _planner(snapshot_subjects: tuple[PromptContextSubject, ...]) -> AvailabilityImportPlanner:
    snapshot = PromptContextSnapshot(
        "availability-context",
        "availability_check",
        datetime(2026, 8, 10).date(),
        {
            "type": "availability_check",
            "as_of_date": "2026-08-10",
            "selected_correlation_refs": [
                item.correlation_ref for item in snapshot_subjects if item.is_target and item.subject_type == "posting"
            ],
        },
        snapshot_subjects,
    )
    return AvailabilityImportPlanner(
        FakeSnapshotRepository(snapshot), FakeSubjectRepository({item.subject_id for item in snapshot_subjects})
    )


def _planner_observation(identifier: str, ref: str) -> dict:
    return {
        "id": identifier,
        "posting_correlation_ref": ref,
        "result": "explicitly_available",
        "observed_at": "2026-08-10T11:00:00Z",
        "evidence_summary": "evidence",
    }


def test_availability_planner_correlation_and_completeness_invariants() -> None:
    subjects = (
        PromptContextSubject("posting-a", "posting", "posting-a", True),
        PromptContextSubject("posting-b", "posting", "posting-b", True),
        PromptContextSubject("context-only", "posting", "posting-c", False),
        PromptContextSubject("wrong-type", "opportunity", "posting-a", True),
    )
    planner = _planner(subjects)
    base = _planner_observation("one", "posting-a")
    missing = planner.plan(_planner_bundle(["posting-a", "posting-b"], [base]))
    assert any(issue.code == "MISSING_AVAILABILITY_RESULT" for issue in missing.issues)
    duplicate = planner.plan(
        _planner_bundle(
            ["posting-a", "posting-b"], [base, _planner_observation("two", "posting-a"), _planner_observation("three", "posting-b")]
        )
    )
    assert any(issue.code == "DUPLICATE_AVAILABILITY_RESULT" for issue in duplicate.issues)
    valid = planner.plan(_planner_bundle(["posting-a", "posting-b"], [base, _planner_observation("two", "posting-b")]))
    assert valid.plan is not None
    assert valid.plan.observations[0].posting_id == "posting-a"
    assert not hasattr(valid.plan.observations[0], "observation")
    absent = planner.plan(_planner_bundle(["posting-a"], [_planner_observation("one", "missing")]))
    assert "UNKNOWN_CORRELATION_REFERENCE" in {issue.code for issue in absent.issues}
    wrong_type = planner.plan(_planner_bundle(["posting-a"], [_planner_observation("one", "wrong-type")]))
    assert "SCOPE_VIOLATION" in {issue.code for issue in wrong_type.issues}
    context_only = planner.plan(_planner_bundle(["posting-a"], [_planner_observation("one", "context-only")]))
    assert "SCOPE_VIOLATION" in {issue.code for issue in context_only.issues}


def test_duplicate_bundle_observation_id_rejected_without_persistence(client) -> None:
    _prepare_context(client)
    bundle = _availability_bundle()
    bundle["observations"].append(dict(bundle["observations"][0]))
    bundle["observations"][1]["posting_correlation_ref"] = "missing"
    report = _import_availability(client, bundle)
    assert report.status == "rejected"
    assert "DUPLICATE_BUNDLE_ID" in {issue.code for issue in report.issues}
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 0


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
        assert (
            session.scalar(
                select(func.count()).select_from(ResearchImportModel).where(ResearchImportModel.import_kind == "availability_check")
            )
            == 1
        )
        assert session.get(PostingModel, posting_id).id == posting_id
    duplicate = _import_availability(client)
    assert duplicate.status == "duplicate"
    assert duplicate.duplicate_of_import_id == first.import_id
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 1
        assert (
            session.scalar(
                select(func.count()).select_from(ResearchImportModel).where(ResearchImportModel.import_kind == "availability_check")
            )
            == 1
        )
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


def test_availability_preserves_subject_counts_and_personal_state(client) -> None:
    posting_id = _prepare_context(client)
    with client.app.state.database.session_factory() as session:
        opportunity_id = session.get(PostingModel, posting_id).opportunity_id
    assessment = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 4, "reasoning": "private"},
    )
    assert assessment.status_code == 201
    status = client.post(f"/api/opportunities/{opportunity_id}/status", json={"status": "shortlisted"})
    assert status.status_code == 200
    before = {
        "companies": client.get("/api/opportunities").json(),
        "assessments": client.get(f"/api/opportunities/{opportunity_id}/assessments/personal/history").json(),
        "decisions": client.get(f"/api/opportunities/{opportunity_id}/decisions").json(),
    }
    with client.app.state.database.session_factory() as session:
        counts_before = [
            session.scalar(select(func.count()).select_from(model)) for model in (CompanyModel, OpportunityModel, PostingModel)
        ]
    assert _import_availability(client).status == "applied"
    with client.app.state.database.session_factory() as session:
        counts_after = [session.scalar(select(func.count()).select_from(model)) for model in (CompanyModel, OpportunityModel, PostingModel)]
    assert counts_after == counts_before
    assert client.get("/api/opportunities").json() == before["companies"]
    assert client.get(f"/api/opportunities/{opportunity_id}/assessments/personal/history").json() == before["assessments"]
    assert client.get(f"/api/opportunities/{opportunity_id}/decisions").json() == before["decisions"]


def test_availability_apply_rolls_back_import_and_observation_on_forced_failure(client) -> None:
    _prepare_context(client)
    from vocation.infrastructure.models import AvailabilityObservationModel

    def fail(_mapper, _connection, _target) -> None:
        raise RuntimeError("forced availability failure")

    event.listen(AvailabilityObservationModel, "before_insert", fail)
    try:
        with pytest.raises(RuntimeError, match="forced availability failure"):
            _import_availability(client)
    finally:
        event.remove(AvailabilityObservationModel, "before_insert", fail)
    with client.app.state.database.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AvailabilityObservationModel)) == 0
        assert (
            session.scalar(
                select(func.count()).select_from(ResearchImportModel).where(ResearchImportModel.import_kind == "availability_check")
            )
            == 0
        )


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
