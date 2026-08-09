from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from tests.test_map_location_resolutions import seed_work_locations
from tests.test_migrations import seed_v020_data
from vocation.application.map import GeocodingResult, MapService
from vocation.infrastructure.map_location_repository import SqlAlchemyMapLocationResolutionRepository


@dataclass
class FakeGeocoder:
    result: GeocodingResult | None
    calls: list[str]

    def geocode(self, query: str) -> GeocodingResult | None:
        self.calls.append(query)
        return self.result


def test_geocode_api_persists_and_replaces_resolution(client, app) -> None:
    database_path = Path(app.state.database.url.removeprefix("sqlite:///"))
    seed_v020_data(database_path)
    seed_work_locations(database_path)
    geocoder = FakeGeocoder(GeocodingResult(48.137, 11.575, "Munich, Germany", "provider-1"), [])
    app.state.map_service = MapService(
        SqlAlchemyMapLocationResolutionRepository(app.state.database.session_factory),
        geocoder,
        clock=lambda: datetime(2026, 8, 10, 12, tzinfo=UTC),
    )

    first = client.post("/api/map/locations/location-1/geocode", json={"query": "Munich"})
    second = client.post("/api/map/locations/location-1/geocode", json={"query": "Munich, Germany"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert geocoder.calls == ["Munich", "Munich, Germany"]
    assert second.json() == {
        "latitude": 48.137,
        "longitude": 11.575,
        "resolution_source": "geocoder",
        "provider_key": "provider-1",
        "resolved_at": "2026-08-10T12:00:00Z",
        "resolved_query": "Munich, Germany",
    }


def test_geocode_api_maps_no_result_and_unknown_location(client, app) -> None:
    database_path = Path(app.state.database.url.removeprefix("sqlite:///"))
    seed_v020_data(database_path)
    seed_work_locations(database_path)
    app.state.map_service = MapService(
        SqlAlchemyMapLocationResolutionRepository(app.state.database.session_factory),
        FakeGeocoder(None, []),
    )

    no_result = client.post("/api/map/locations/location-1/geocode", json={"query": "nowhere"})
    unknown = client.post("/api/map/locations/missing/geocode", json={"query": "Berlin"})

    assert no_result.status_code == 404
    assert no_result.json()["detail"] == "No geocoding result found."
    assert unknown.status_code == 404
    assert "does not exist" in unknown.json()["detail"]
