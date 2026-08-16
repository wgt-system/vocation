from __future__ import annotations

from typing import Any

import httpx

from vocation.application.map import Geocoder, GeocodingResult


class OrientationGeocoderError(RuntimeError):
    """Base class for deterministic Orientation geocoder failures."""


class OrientationGeocoderUnavailableError(OrientationGeocoderError):
    """The configured Orientation service could not provide place search."""


class OrientationGeocoderResponseError(OrientationGeocoderError):
    """The Orientation place-search response did not match the accepted shape."""


class OrientationGeocoder(Geocoder):
    def __init__(self, base_url: str, *, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        )
        self._owns_client = client is None

    def geocode(self, query: str) -> GeocodingResult | None:
        query = query.strip()
        if not query:
            raise ValueError("Geocoding query must be nonempty.")
        try:
            response = self._client.get("/api/v1/places/search", params={"q": query, "limit": 1})
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise OrientationGeocoderUnavailableError("Orientation place search is unavailable.") from error
        try:
            payload = response.json()
        except ValueError as error:
            raise OrientationGeocoderResponseError("Orientation place-search response is not valid JSON.") from error
        return self._parse(payload)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    @staticmethod
    def _parse(payload: Any) -> GeocodingResult | None:
        if not isinstance(payload, dict):
            raise OrientationGeocoderResponseError("Orientation place-search response must be a JSON object.")
        places = payload.get("places")
        if not isinstance(places, list):
            raise OrientationGeocoderResponseError("Orientation place-search response must contain a places array.")
        if not places:
            return None

        place = places[0]
        if not isinstance(place, dict):
            raise OrientationGeocoderResponseError("Orientation place result must be a JSON object.")

        provider_reference = place.get("providerReference")
        display_label = place.get("displayLabel")
        coordinate = place.get("coordinate")
        if not isinstance(provider_reference, str) or not provider_reference.strip():
            raise OrientationGeocoderResponseError("Orientation place result has no valid provider reference.")
        if not isinstance(display_label, str) or not display_label.strip():
            raise OrientationGeocoderResponseError("Orientation place result has no valid display label.")
        if not isinstance(coordinate, dict):
            raise OrientationGeocoderResponseError("Orientation place result has no valid coordinate.")

        latitude = OrientationGeocoder._finite_float(coordinate.get("latitude"), "latitude")
        longitude = OrientationGeocoder._finite_float(coordinate.get("longitude"), "longitude")
        if not -90 <= latitude <= 90:
            raise OrientationGeocoderResponseError("Orientation place result has an out-of-range latitude.")
        if not -180 <= longitude <= 180:
            raise OrientationGeocoderResponseError("Orientation place result has an out-of-range longitude.")

        return GeocodingResult(
            latitude=latitude,
            longitude=longitude,
            resolved_query=display_label.strip(),
            provider_key=provider_reference.strip(),
        )

    @staticmethod
    def _finite_float(value: Any, field: str) -> float:
        if isinstance(value, bool):
            raise OrientationGeocoderResponseError(f"Orientation place result has no valid {field}.")
        try:
            result = float(value)
        except (TypeError, ValueError) as error:
            raise OrientationGeocoderResponseError(f"Orientation place result has no valid {field}.") from error
        if result != result or result in {float("inf"), float("-inf")}:
            raise OrientationGeocoderResponseError(f"Orientation place result has no finite {field}.")
        return result
