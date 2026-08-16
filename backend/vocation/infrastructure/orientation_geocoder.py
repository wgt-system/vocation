from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from vocation.application.map import Geocoder, GeocodingResult

OrientationTransport = Callable[[str, float], bytes]


class OrientationGeocoderError(RuntimeError):
    """Base class for deterministic Orientation geocoder failures."""


class OrientationGeocoderUnavailableError(OrientationGeocoderError):
    """The configured Orientation service could not provide place search."""


class OrientationGeocoderResponseError(OrientationGeocoderError):
    """The Orientation place-search response did not match the accepted shape."""


class OrientationGeocoder(Geocoder):
    MAX_RESPONSE_BYTES = 1_048_576
    REQUEST_TIMEOUT_SECONDS = 10.0

    def __init__(self, base_url: str, *, transport: OrientationTransport | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._transport = transport or self._fetch

    def geocode(self, query: str) -> GeocodingResult | None:
        query = query.strip()
        if not query:
            raise ValueError("Geocoding query must be nonempty.")

        url = f"{self._base_url}/api/v1/places/search?{urlencode({'q': query, 'limit': 1})}"
        try:
            raw_payload = self._transport(url, self.REQUEST_TIMEOUT_SECONDS)
        except OrientationGeocoderError:
            raise
        except (OSError, TimeoutError) as error:
            raise OrientationGeocoderUnavailableError("Orientation place search is unavailable.") from error

        try:
            payload = json.loads(raw_payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise OrientationGeocoderResponseError("Orientation place-search response is not valid JSON.") from error
        return self._parse(payload)

    def close(self) -> None:
        """Keep application composition symmetric with replaceable HTTP adapters."""

    @classmethod
    def _fetch(cls, url: str, timeout_seconds: float) -> bytes:
        request = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - trusted configured local Orientation URL
                payload = response.read(cls.MAX_RESPONSE_BYTES + 1)
        except (HTTPError, URLError, OSError, TimeoutError) as error:
            raise OrientationGeocoderUnavailableError("Orientation place search is unavailable.") from error

        if len(payload) > cls.MAX_RESPONSE_BYTES:
            raise OrientationGeocoderResponseError("Orientation place-search response is too large.")
        return payload

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
