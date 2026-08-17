from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from tests.test_imports import valid_bundle
from vocation.infrastructure.models import AvailabilityObservationModel, OpportunityModel, PostingModel, WorkLocationModel


def seed_market(client) -> tuple[str, str, str]:
    imported = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    with client.app.state.database.session_factory.begin() as session:
        opportunity = session.get(OpportunityModel, opportunity_id)
        for location_id, label in (("map-location-1", "Berlin"), ("map-location-2", "Munich")):
            session.add(
                WorkLocationModel(
                    id=location_id,
                    opportunity_id=opportunity_id,
                    label=label,
                    city=label,
                    region="BE",
                    country_code="DE",
                    precision="city",
                    source_reference_id=opportunity.source_reference_id,
                    observed_at=datetime(2025, 1, 1),
                )
            )
        posting_id = session.scalar(select(PostingModel.id).where(PostingModel.opportunity_id == opportunity_id))
    return imported["import_id"], opportunity_id, posting_id


def test_map_locations_manual_resolution_and_delete(client) -> None:
    _, opportunity_id, _ = seed_market(client)
    locations = client.get("/api/map/locations")
    assert locations.status_code == 200
    assert len(locations.json()) == 3
    assert locations.json()[0]["opportunity_id"] == opportunity_id
    location_id = locations.json()[0]["work_location_id"]
    assert locations.json()[0]["resolution"] is None

    resolved = client.put(
        f"/api/map/locations/{location_id}/resolution",
        json={"latitude": 52.52, "longitude": 13.405, "resolved_query": "Berlin"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["resolution_source"] == "manual"
    assert client.get("/api/map/locations").json()[0]["resolution"]["latitude"] == 52.52
    assert client.delete(f"/api/map/locations/{location_id}/resolution").status_code == 204
    assert client.get("/api/map/locations").json()[0]["resolution"] is None
    assert (
        client.put(
            "/api/map/locations/missing/resolution",
            json={"latitude": 0, "longitude": 0, "resolved_query": "x"},
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/api/map/locations/{location_id}/resolution",
            json={"latitude": 91, "longitude": 0, "resolved_query": "x"},
        ).status_code
        == 422
    )


def test_map_projection_is_resolved_scoped_and_includes_availability_and_groups(client) -> None:
    import_id, opportunity_id, posting_id = seed_market(client)
    locations = client.get("/api/map/locations").json()
    assert len(locations) == 3
    first_location, second_location = locations[:2]
    assert (
        client.put(
            f"/api/map/locations/{first_location['work_location_id']}/resolution",
            json={"latitude": 50.0, "longitude": 10.0, "resolved_query": first_location["label"]},
        ).status_code
        == 200
    )

    group = client.post("/api/groups", json={"name": "Wave", "description": None, "group_type": "application_wave"}).json()
    assert client.post(f"/api/groups/{group['id']}/memberships", json={"opportunity_id": opportunity_id}).status_code == 200
    with client.app.state.database.session_factory.begin() as session:
        session.add(
            AvailabilityObservationModel(
                id="map-availability-1",
                import_id=import_id,
                bundle_local_id="map-availability-1",
                posting_id=posting_id,
                result="explicitly_available",
                observed_at=datetime(2026, 8, 9, 12, 0),
                recorded_at=datetime(2026, 8, 9, 12, 1),
                evidence_summary="Still listed",
            )
        )

    projection = client.post("/api/map/projection", json={"opportunity_ids": [opportunity_id]}).json()
    assert [item["work_location_id"] for item in projection] == [first_location["work_location_id"]]

    assert (
        client.put(
            f"/api/map/locations/{second_location['work_location_id']}/resolution",
            json={"latitude": 50.0, "longitude": 10.0, "resolved_query": second_location["label"]},
        ).status_code
        == 200
    )
    projection = client.post("/api/map/projection", json={"opportunity_ids": [opportunity_id]}).json()
    assert len(projection) == 2
    assert {item["work_location_id"] for item in projection} == {
        first_location["work_location_id"],
        second_location["work_location_id"],
    }
    assert all(item["availability"] == "available" for item in projection)
    assert all(item["groups"] == [{"group_id": group["id"], "name": "Wave", "group_type": "application_wave"}] for item in projection)

    empty = client.post("/api/map/projection", json={"opportunity_ids": []})
    assert empty.status_code == 200
    assert empty.json() == []
