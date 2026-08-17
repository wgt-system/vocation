from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class PublicationWorkLocation:
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: str


@dataclass(frozen=True)
class PublicationOpportunitySource:
    opportunity_ref: str
    title: str
    company_ref: str
    company_name: str
    work_locations: tuple[PublicationWorkLocation, ...]
    posting_count: int


class OpportunityOverviewPublicationRepository(Protocol):
    def load_opportunities(self) -> tuple[PublicationOpportunitySource, ...]: ...


@dataclass(frozen=True)
class PublicationMapFeatureSource:
    feature_ref: str
    opportunity_ref: str
    title: str
    company_ref: str
    company_name: str
    location_label: str
    precision: str
    latitude: float
    longitude: float


class MapProjectionPublicationRepository(Protocol):
    def load_features(self) -> tuple[PublicationMapFeatureSource, ...]: ...


@dataclass(frozen=True)
class PublishedCompany:
    company_ref: str
    name: str


@dataclass(frozen=True)
class PublishedWorkLocation:
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: str


@dataclass(frozen=True)
class PublishedOpportunity:
    opportunity_ref: str
    title: str
    company: PublishedCompany
    work_locations: tuple[PublishedWorkLocation, ...]
    posting_count: int


@dataclass(frozen=True)
class PublicationMetadata:
    publication_ref: str
    generated_at: str


@dataclass(frozen=True)
class PublishedOpportunityOverview:
    capability: str
    contract_version: str
    publication: PublicationMetadata
    opportunities: tuple[PublishedOpportunity, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "capability": self.capability,
            "contract_version": self.contract_version,
            "publication": {
                "publication_ref": self.publication.publication_ref,
                "generated_at": self.publication.generated_at,
            },
            "opportunities": [
                {
                    "opportunity_ref": opportunity.opportunity_ref,
                    "title": opportunity.title,
                    "company": {
                        "company_ref": opportunity.company.company_ref,
                        "name": opportunity.company.name,
                    },
                    "work_locations": [
                        {
                            "label": location.label,
                            "city": location.city,
                            "region": location.region,
                            "country_code": location.country_code,
                            "precision": location.precision,
                        }
                        for location in opportunity.work_locations
                    ],
                    "posting_count": opportunity.posting_count,
                }
                for opportunity in self.opportunities
            ],
        }


@dataclass(frozen=True)
class PublishedMapCompany:
    company_ref: str
    name: str


@dataclass(frozen=True)
class PublishedMapFeature:
    feature_ref: str
    opportunity_ref: str
    title: str
    company: PublishedMapCompany
    location_label: str
    precision: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class PublishedMapProjection:
    capability: str
    contract_version: str
    publication: PublicationMetadata
    features: tuple[PublishedMapFeature, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "capability": self.capability,
            "contract_version": self.contract_version,
            "publication": {
                "publication_ref": self.publication.publication_ref,
                "generated_at": self.publication.generated_at,
            },
            "features": [
                {
                    "feature_ref": feature.feature_ref,
                    "opportunity_ref": feature.opportunity_ref,
                    "title": feature.title,
                    "company": {
                        "company_ref": feature.company.company_ref,
                        "name": feature.company.name,
                    },
                    "work_location": {
                        "label": feature.location_label,
                        "precision": feature.precision,
                    },
                    "coordinates": {
                        "latitude": feature.latitude,
                        "longitude": feature.longitude,
                    },
                }
                for feature in self.features
            ],
        }


def _optional_text_key(value: str | None) -> tuple[bool, str]:
    return (value is None, "" if value is None else value.casefold())


class OpportunityOverviewPublicationService:
    def __init__(
        self,
        repository: OpportunityOverviewPublicationRepository,
        *,
        ref_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._ref_factory = ref_factory or (lambda: str(uuid4()))
        self._clock = clock or (lambda: datetime.now(UTC))

    def generate(self) -> PublishedOpportunityOverview:
        sources = sorted(
            self._repository.load_opportunities(),
            key=lambda item: (item.company_name.casefold(), item.title.casefold(), item.opportunity_ref),
        )
        opportunities = tuple(
            PublishedOpportunity(
                opportunity_ref=item.opportunity_ref,
                title=item.title,
                company=PublishedCompany(item.company_ref, item.company_name),
                work_locations=tuple(
                    PublishedWorkLocation(
                        label=location.label,
                        city=location.city,
                        region=location.region,
                        country_code=location.country_code,
                        precision=location.precision,
                    )
                    for location in sorted(
                        item.work_locations,
                        key=lambda location: (
                            location.label.casefold(),
                            *_optional_text_key(location.city),
                            *_optional_text_key(location.region),
                            *_optional_text_key(location.country_code),
                            location.precision,
                        ),
                    )
                ),
                posting_count=item.posting_count,
            )
            for item in sources
        )
        generated_at = self._clock()
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=UTC)
        generated_at_text = generated_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
        return PublishedOpportunityOverview(
            capability="vocation.opportunity_overview",
            contract_version="1.0",
            publication=PublicationMetadata(self._ref_factory(), generated_at_text),
            opportunities=opportunities,
        )


class MapProjectionPublicationService:
    def __init__(
        self,
        repository: MapProjectionPublicationRepository,
        *,
        ref_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._ref_factory = ref_factory or (lambda: str(uuid4()))
        self._clock = clock or (lambda: datetime.now(UTC))

    def generate(self) -> PublishedMapProjection:
        sources = sorted(
            self._repository.load_features(),
            key=lambda item: (item.company_name.casefold(), item.title.casefold(), item.location_label.casefold(), item.feature_ref),
        )
        generated_at = self._clock()
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=UTC)
        return PublishedMapProjection(
            capability="vocation.map_projection",
            contract_version="1.0",
            publication=PublicationMetadata(
                self._ref_factory(),
                generated_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            ),
            features=tuple(
                PublishedMapFeature(
                    feature_ref=item.feature_ref,
                    opportunity_ref=item.opportunity_ref,
                    title=item.title,
                    company=PublishedMapCompany(item.company_ref, item.company_name),
                    location_label=item.location_label,
                    precision=item.precision,
                    latitude=item.latitude,
                    longitude=item.longitude,
                )
                for item in sources
            ),
        )
