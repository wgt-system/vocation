from __future__ import annotations

from datetime import UTC
from typing import cast

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    GeocodeResolutionPayload,
    GroupType,
    MapGroupMembershipResponse,
    MapLocationResponse,
    MapProjectionFeatureResponse,
    MapProjectionPayload,
    MapResolutionPayload,
    MapResolutionResponse,
    TrackingStatus,
)
from vocation.application.map import GeocodingNoResultError, GeocodingQueryError, MapLocationContext, MapProjectionFeature, MapService
from vocation.infrastructure.map_location_repository import (
    MapLocationResolutionValidationError,
    WorkLocationNotFoundError,
)
from vocation.infrastructure.orientation_geocoder import (
    OrientationGeocoderResponseError,
    OrientationGeocoderUnavailableError,
)

router = APIRouter(prefix="/api/map", tags=["map"])


def _service(request: Request) -> MapService:
    return request.app.state.map_service


def _resolution(resolution) -> MapResolutionResponse | None:
    if resolution is None:
        return None
    resolved_at = resolution.resolved_at
    if resolved_at.tzinfo is None:
        resolved_at = resolved_at.replace(tzinfo=UTC)
    return MapResolutionResponse(
        latitude=resolution.latitude,
        longitude=resolution.longitude,
        resolution_source=resolution.resolution_source,
        provider_key=resolution.provider_key,
        resolved_at=resolved_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        resolved_query=resolution.resolved_query,
    )


def _location(location: MapLocationContext) -> MapLocationResponse:
    return MapLocationResponse(
        work_location_id=location.work_location_id,
        opportunity_id=location.opportunity_id,
        title=location.title,
        company_id=location.company_id,
        company_name=location.company_name,
        label=location.label,
        city=location.city,
        region=location.region,
        country_code=location.country_code,
        precision=location.precision,
        resolution=_resolution(location.resolution),
    )


def _feature(feature: MapProjectionFeature) -> MapProjectionFeatureResponse:
    return MapProjectionFeatureResponse(
        feature_id=feature.feature_id,
        work_location_id=feature.work_location_id,
        opportunity_id=feature.opportunity_id,
        company_id=feature.company_id,
        title=feature.title,
        company_name=feature.company_name,
        location_label=feature.location_label,
        latitude=feature.latitude,
        longitude=feature.longitude,
        precision=feature.precision,
        tracking_status=cast(TrackingStatus, feature.tracking_status),
        availability=feature.availability,
        groups=[
            MapGroupMembershipResponse(group_id=group.group_id, name=group.name, group_type=cast(GroupType, group.group_type))
            for group in feature.groups
        ],
    )


@router.get("/locations", response_model=list[MapLocationResponse])
def list_map_locations(request: Request) -> list[MapLocationResponse]:
    return [_location(location) for location in _service(request).list_locations()]


@router.put("/locations/{work_location_id}/resolution", response_model=MapResolutionResponse)
def set_resolution(work_location_id: str, payload: MapResolutionPayload, request: Request) -> MapResolutionResponse:
    try:
        return _resolution(
            _service(request).set_manual_resolution(work_location_id, payload.latitude, payload.longitude, payload.resolved_query)
        )  # type: ignore[return-value]
    except WorkLocationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except MapLocationResolutionValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete("/locations/{work_location_id}/resolution", status_code=204)
def delete_resolution(work_location_id: str, request: Request) -> None:
    try:
        _service(request).delete_resolution(work_location_id)
    except WorkLocationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/locations/{work_location_id}/geocode", response_model=MapResolutionResponse)
def geocode_location(work_location_id: str, payload: GeocodeResolutionPayload, request: Request) -> MapResolutionResponse:
    try:
        return _resolution(_service(request).geocode_resolution(work_location_id, payload.query))  # type: ignore[return-value]
    except (LookupError, GeocodingNoResultError) as error:
        status = 404
        detail = str(error)
        if isinstance(error, GeocodingNoResultError):
            detail = "No geocoding result found."
        raise HTTPException(status_code=status, detail=detail) from error
    except (GeocodingQueryError, OrientationGeocoderResponseError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except OrientationGeocoderUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/projection", response_model=list[MapProjectionFeatureResponse])
def map_projection(payload: MapProjectionPayload, request: Request) -> list[MapProjectionFeatureResponse]:
    return [_feature(feature) for feature in _service(request).projection(payload.opportunity_ids)]
