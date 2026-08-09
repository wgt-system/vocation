from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

AvailabilityCheckResult = Literal[
    "explicitly_available",
    "explicitly_unavailable",
    "temporarily_unreachable",
    "not_found",
    "indeterminate",
]
DerivedAvailability = Literal["available", "unavailable", "uncertain", "unknown"]


@dataclass(frozen=True)
class AvailabilityObservation:
    id: str
    posting_id: str
    result: AvailabilityCheckResult
    observed_at: datetime
    recorded_at: datetime
    evidence_summary: str


@dataclass(frozen=True)
class PostingAvailability:
    availability: DerivedAvailability
    last_checked_at: datetime | None
    age_days: int | None


@dataclass(frozen=True)
class OpportunityAvailability:
    availability: DerivedAvailability
    last_checked_at: datetime | None
    age_days: int | None


def _utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _age_days(now: datetime, checked_at: datetime | None) -> int | None:
    if checked_at is None:
        return None
    elapsed = (_utc(now).astimezone(UTC) - _utc(checked_at).astimezone(UTC)).total_seconds()
    return max(0, int(elapsed // 86_400))


class AvailabilityEvaluator:
    def posting(self, observations: tuple[AvailabilityObservation, ...], now: datetime) -> PostingAvailability:
        if not observations:
            return PostingAvailability("unknown", None, None)
        latest = max(observations, key=lambda item: (_utc(item.observed_at), _utc(item.recorded_at), item.id))
        mapping: dict[AvailabilityCheckResult, DerivedAvailability] = {
            "explicitly_available": "available",
            "explicitly_unavailable": "unavailable",
            "temporarily_unreachable": "uncertain",
            "not_found": "uncertain",
            "indeterminate": "uncertain",
        }
        availability = mapping[latest.result]
        return PostingAvailability(availability, latest.observed_at, _age_days(now, latest.observed_at))

    def opportunity(
        self,
        posting_observations: tuple[tuple[AvailabilityObservation, ...], ...],
        now: datetime,
    ) -> OpportunityAvailability:
        assessments = tuple(self.posting(observations, now) for observations in posting_observations)
        if not assessments:
            return OpportunityAvailability("unknown", None, None)
        states = {assessment.availability for assessment in assessments}
        if "available" in states:
            availability: DerivedAvailability = "available"
        elif "uncertain" in states:
            availability = "uncertain"
        elif "unknown" in states:
            availability = "unknown"
        else:
            availability = "unavailable"
        checked = [observation.observed_at for observations in posting_observations for observation in observations]
        last_checked_at = max(checked) if checked else None
        return OpportunityAvailability(availability, last_checked_at, _age_days(now, last_checked_at))
