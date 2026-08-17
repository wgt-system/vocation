from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

from vocation.domain.availability import AvailabilityEvaluator, AvailabilityObservation

ComparisonObservationType = Literal[
    "technology_requirement",
    "task",
    "seniority",
    "experience_requirement",
    "work_model",
    "salary",
]
ComparisonSubjectType = Literal["opportunity", "posting"]


@dataclass(frozen=True)
class ComparisonWorkLocation:
    label: str
    precision: str


@dataclass(frozen=True)
class ComparisonGroup:
    group_id: str
    name: str
    group_type: str


@dataclass(frozen=True)
class ComparisonObservation:
    id: str
    subject_type: ComparisonSubjectType
    subject_id: str
    observation_type: ComparisonObservationType
    value: Any
    observed_at: datetime
    evidence_summary: str | None


@dataclass(frozen=True)
class ComparisonExternalAssessment:
    id: str
    criterion_id: str
    value: Any
    reasoning: str | None
    created_at: datetime


@dataclass(frozen=True)
class ComparisonPersonalAssessment:
    criterion_id: str
    value: Any
    reasoning: str | None
    created_at: datetime


@dataclass(frozen=True)
class ComparisonCriterion:
    criterion_id: str
    display_name: str
    display_order: int


@dataclass(frozen=True)
class ComparisonOpportunity:
    opportunity_id: str
    title: str
    company_id: str
    company_name: str
    work_locations: tuple[ComparisonWorkLocation, ...]
    tracking_status: str
    groups: tuple[ComparisonGroup, ...]
    postings: tuple[str, ...]
    observations: tuple[ComparisonObservation, ...]
    availability_observations: tuple[tuple[AvailabilityObservation, ...], ...]
    personal_assessments: tuple[ComparisonPersonalAssessment, ...]
    external_assessments: tuple[ComparisonExternalAssessment, ...]


class ComparisonRepository(Protocol):
    def get_many(self, opportunity_ids: Sequence[str]) -> list[ComparisonOpportunity]: ...
    def criteria(self, criterion_ids: Sequence[str]) -> list[ComparisonCriterion]: ...


class ComparisonInputError(ValueError):
    pass


class ComparisonOpportunityNotFound(LookupError):
    pass


_OBSERVATION_TYPES: tuple[ComparisonObservationType, ...] = (
    "technology_requirement",
    "task",
    "seniority",
    "experience_requirement",
    "work_model",
    "salary",
)


@dataclass(frozen=True)
class ComparisonDimensionValue:
    value: Any
    subject_type: ComparisonSubjectType
    subject_id: str
    observed_at: datetime
    evidence_summary: str | None


@dataclass(frozen=True)
class ComparisonDimensionCell:
    state: Literal["present", "missing"]
    values: tuple[ComparisonDimensionValue, ...]


@dataclass(frozen=True)
class ComparisonOpportunityView:
    opportunity_id: str
    title: str
    company_id: str
    company_name: str
    work_locations: tuple[ComparisonWorkLocation, ...]
    tracking_status: str
    availability: str
    availability_last_checked_at: datetime | None
    availability_age_days: int | None
    groups: tuple[ComparisonGroup, ...]
    research_dimensions: dict[str, ComparisonDimensionCell]
    personal_assessments: tuple[ComparisonPersonalAssessment, ...]
    external_assessments: tuple[ComparisonExternalAssessment, ...]


@dataclass(frozen=True)
class OpportunityComparison:
    opportunities: tuple[ComparisonOpportunityView, ...]
    assessment_criteria: tuple[ComparisonCriterion, ...]


class OpportunityComparisonService:
    def __init__(self, repository: ComparisonRepository, *, clock=None):
        self.repository = repository
        self.clock = clock

    def compare(self, opportunity_ids: Sequence[str]) -> OpportunityComparison:
        requested = list(opportunity_ids)
        if len(requested) < 2 or len(requested) > 4:
            raise ComparisonInputError("Comparison requires between 2 and 4 opportunities.")
        if len(requested) != len(set(requested)):
            raise ComparisonInputError("Comparison opportunity IDs must be unique.")

        records = self.repository.get_many(requested)
        by_id = {record.opportunity_id: record for record in records}
        missing = next((opportunity_id for opportunity_id in requested if opportunity_id not in by_id), None)
        if missing is not None:
            raise ComparisonOpportunityNotFound(missing)

        now = self.clock() if self.clock is not None else datetime.now(UTC)
        evaluator = AvailabilityEvaluator()
        views: list[ComparisonOpportunityView] = []
        criterion_ids: set[str] = set()
        for opportunity_id in requested:
            record = by_id[opportunity_id]
            aggregate = evaluator.opportunity(record.availability_observations, now)
            dimensions = self._dimensions(record.observations)
            criterion_ids.update(item.criterion_id for item in record.personal_assessments)
            criterion_ids.update(item.criterion_id for item in record.external_assessments)
            views.append(
                ComparisonOpportunityView(
                    opportunity_id=record.opportunity_id,
                    title=record.title,
                    company_id=record.company_id,
                    company_name=record.company_name,
                    work_locations=record.work_locations,
                    tracking_status=record.tracking_status,
                    availability=aggregate.availability,
                    availability_last_checked_at=aggregate.last_checked_at,
                    availability_age_days=aggregate.age_days,
                    groups=record.groups,
                    research_dimensions=dimensions,
                    personal_assessments=record.personal_assessments,
                    external_assessments=record.external_assessments,
                )
            )
        criteria = tuple(sorted(self.repository.criteria(tuple(criterion_ids)), key=lambda item: (item.display_order, item.criterion_id)))
        return OpportunityComparison(tuple(views), criteria)

    @staticmethod
    def _dimensions(observations: Sequence[ComparisonObservation]) -> dict[str, ComparisonDimensionCell]:
        result: dict[str, ComparisonDimensionCell] = {}
        for observation_type in _OBSERVATION_TYPES:
            matching = [item for item in observations if item.observation_type == observation_type]
            representatives: dict[str, ComparisonObservation] = {}
            for item in matching:
                key = json.dumps(item.value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                previous = representatives.get(key)
                if previous is None or (item.observed_at, item.id) > (previous.observed_at, previous.id):
                    representatives[key] = item
            ordered = sorted(representatives.values(), key=lambda item: (item.observed_at, item.id), reverse=True)
            result[observation_type] = ComparisonDimensionCell(
                "present" if ordered else "missing",
                tuple(
                    ComparisonDimensionValue(item.value, item.subject_type, item.subject_id, item.observed_at, item.evidence_summary)
                    for item in ordered
                ),
            )
        return result
