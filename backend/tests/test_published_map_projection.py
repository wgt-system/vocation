from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from tests.test_imports import import_bundle, valid_bundle
from vocation.application.publication import (
    MapProjectionPublicationService,
    PublicationMapFeatureSource,
)

ROOT = Path(__file__).resolve().parents[2]


class FakeMapPublicationRepository:
    def __init__(self, features: tuple[PublicationMapFeatureSource, ...]) -> None:
        self.features = features

    def load_features(self) -> tuple[PublicationMapFeatureSource, ...]:
        return self.features


def feature(
    feature_ref: str,
    opportunity_ref: str,
    title: str,
    company_ref: str,
    company_name: str,
    label: str,
) -> PublicationMapFeatureSource:
    return PublicationMapFeatureSource(
        feature_ref,
        opportunity_ref,
        title,
        company_ref,
        company_name,
        label,
        "city",
        53.5,
        10.0,
    )


def test_map_publication_is_deterministic_mapped_only_and_opaque() -> None:
    service = MapProjectionPublicationService(
        FakeMapPublicationRepository(
            (
                feature("wl-2", "opp-b", "Beta", "company-b", "Zeta", "Office"),
                feature("wl-3", "opp-a", "Alpha", "company-a", "Alpha", "Second"),
                feature("wl-1", "opp-a", "Alpha", "company-a", "Alpha", "First"),
            )
        ),
        ref_factory=lambda: "publication-ref",
        clock=lambda: datetime(2026, 8, 13, 12, 0, tzinfo=UTC),
    )

    artifact = service.generate().as_dict()

    assert artifact["capability"] == "vocation.map_projection"
    assert artifact["contract_version"] == "1.0"
    assert artifact["publication"] == {"publication_ref": "publication-ref", "generated_at": "2026-08-13T12:00:00Z"}
    assert [item["feature_ref"] for item in artifact["features"]] == ["wl-1", "wl-3", "wl-2"]
    assert artifact["features"][0]["coordinates"] == {"latitude": 53.5, "longitude": 10.0}
    assert "id" not in json.dumps(artifact)
    assert "tracking_status" not in json.dumps(artifact)


def test_empty_map_publication_has_no_features() -> None:
    service = MapProjectionPublicationService(FakeMapPublicationRepository(()), ref_factory=lambda: "r")
    assert service.generate().as_dict()["features"] == []


def test_published_map_endpoint_validates_schema_and_is_hidden_from_openapi(client) -> None:
    assert import_bundle(client, valid_bundle()).json()["status"] == "applied"
    with client.app.state.database.session_factory.begin() as session:
        from vocation.infrastructure.models import MapLocationResolutionModel, WorkLocationModel

        location = session.query(WorkLocationModel).first()
        session.add(
            MapLocationResolutionModel(
                work_location_id=location.id,
                latitude=53.5,
                longitude=10.0,
                resolution_source="manual",
                provider_key=None,
                resolved_at=datetime(2026, 8, 13, tzinfo=UTC),
                resolved_query="Hamburg",
            )
        )

    response = client.get("/published/v1/map-projection")
    assert response.status_code == 200
    schema = json.loads((ROOT / "schemas" / "published-map-projection-v1.schema.json").read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(response.json()))
    assert len(response.json()["features"]) == 1
    assert "/published/v1/map-projection" not in client.app.openapi()["paths"]
