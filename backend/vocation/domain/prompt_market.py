from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

SubjectType = Literal["company", "opportunity", "posting"]


@dataclass(frozen=True)
class MarketLocation:
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: str
    source_url: str | None


@dataclass(frozen=True)
class MarketCompany:
    subject_id: str
    name: str
    source_url: str | None


@dataclass(frozen=True)
class MarketOpportunity:
    subject_id: str
    company_id: str
    title: str
    locations: tuple[MarketLocation, ...]
    source_url: str | None


@dataclass(frozen=True)
class MarketPosting:
    subject_id: str
    company_id: str
    opportunity_id: str
    title: str
    external_posting_id: str | None
    canonical_url: str
    published_at: str | None
    observed_at: datetime


@dataclass(frozen=True)
class MarketObservation:
    subject_type: SubjectType
    subject_id: str
    observation_type: str
    value: Any
    observed_at: datetime
    confidence: float | None
    evidence_summary: str | None
    source_url: str | None


@dataclass(frozen=True)
class MarketAssessment:
    subject_type: SubjectType
    subject_id: str
    criterion_id: str
    value: Any
    created_at: datetime
    reasoning: str | None
    source_urls: tuple[str, ...]


@dataclass(frozen=True)
class MarketDuplicateCase:
    case_id: str
    subject_type: Literal["opportunity", "posting"]
    left_subject_id: str
    right_subject_id: str
    evidence_summary: str
    confidence: float | None
    source_urls: tuple[str, ...]


@dataclass(frozen=True)
class PromptMarket:
    companies: tuple[MarketCompany, ...]
    opportunities: tuple[MarketOpportunity, ...]
    postings: tuple[MarketPosting, ...]
    observations: tuple[MarketObservation, ...]
    assessments: tuple[MarketAssessment, ...]
    duplicate_cases: tuple[MarketDuplicateCase, ...]
