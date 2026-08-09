from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from vocation.domain.availability import AvailabilityEvaluator, AvailabilityObservation, DerivedAvailability
from vocation.domain.map_locations import MapLocationResolution


@dataclass(frozen=True)
class GeocodingResult:
    latitude: float
    longitude: float
    resolved_query: str
    provider_key: str


class Geocoder(Protocol):
    def geocode(self, query: str) -> GeocodingResult | None: ...


@dataclass(frozen=True)
class MapGroupMembership:
    group_id: str
    name: str
    group_type: str


@dataclass(frozen=True)
class MapLocationContext:
    work_location_id: str
    opportunity_id: str
    company_id: str
    title: str
    company_name: str
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: str
    tracking_status: str
    resolution: MapLocationResolution | None
    availability_observations: tuple[tuple[AvailabilityObservation, ...], ...]
    groups: tuple[MapGroupMembership, ...]


@dataclass(frozen=True)
class MapProjectionFeature:
    feature_id: str
    work_location_id: str
    opportunity_id: str
    company_id: str
    title: str
    company_name: str
    location_label: str
    latitude: float
    longitude: float
    precision: str
    tracking_status: str
    availability: DerivedAvailability
    groups: tuple[MapGroupMembership, ...]


class MapRepository(Protocol):
    def list_locations(self) -> list[MapLocationContext]: ...
    def get_location(self, work_location_id: str) -> MapLocationContext | None: ...
    def list_locations_for_opportunities(self, opportunity_ids: Sequence[str]) -> list[MapLocationContext]: ...
    def set_resolution(self, resolution: MapLocationResolution) -> MapLocationResolution: ...
    def delete_resolution(self, work_location_id: str) -> None: ...


class MapService:
    def __init__(self, repository: MapRepository, clock: Callable[[], datetime] | None = None):
        self.repository = repository
        self.clock = clock or (lambda: datetime.now(UTC))

    def list_locations(self) -> list[MapLocationContext]:
        return self.repository.list_locations()

    def set_manual_resolution(self, work_location_id: str, latitude: float, longitude: float, resolved_query: str) -> MapLocationResolution:
        return self.repository.set_resolution(
            MapLocationResolution(work_location_id, latitude, longitude, "manual", None, self.clock(), resolved_query)
        )

    def delete_resolution(self, work_location_id: str) -> None:
        self.repository.delete_resolution(work_location_id)

    def projection(self, opportunity_ids: Sequence[str]) -> list[MapProjectionFeature]:
        now = self.clock()
        evaluator = AvailabilityEvaluator()
        features: list[MapProjectionFeature] = []
        for location in self.repository.list_locations_for_opportunities(opportunity_ids):
            if location.resolution is None:
                continue
            availability = evaluator.opportunity(location.availability_observations, now).availability
            features.append(
                MapProjectionFeature(
                    feature_id=location.work_location_id,
                    work_location_id=location.work_location_id,
                    opportunity_id=location.opportunity_id,
                    company_id=location.company_id,
                    title=location.title,
                    company_name=location.company_name,
                    location_label=location.label,
                    latitude=location.resolution.latitude,
                    longitude=location.resolution.longitude,
                    precision=location.precision,
                    tracking_status=location.tracking_status,
                    availability=availability,
                    groups=location.groups,
                )
            )
        return features
