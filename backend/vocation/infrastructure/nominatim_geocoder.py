from __future__ import annotations

import time
from collections.abc import Callable
from threading import Lock
from typing import Any

import httpx

from vocation.application.map import Geocoder, GeocodingResult


class NominatimError(RuntimeError):
    """Base class for deterministic Nominatim adapter failures."""


class NominatimUnavailableError(NominatimError):
    """The configured provider could not be reached or returned an HTTP error."""


class NominatimResponseError(NominatimError):
    """The provider response did not match the expected jsonv2 shape."""


class NominatimGeocoder(Geocoder):
    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.Client | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        user_agent: str = "Vocation/1.0 (local job-market application)",
    ) -> None:
        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"User-Agent": user_agent},
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        )
        self._client.headers["User-Agent"] = user_agent
        self._owns_client = client is None
        self._monotonic = monotonic
        self._sleep = sleep
        self._next_request_at = 0.0
        self._rate_limit_lock = Lock()

    def geocode(self, query: str) -> GeocodingResult | None:
        if not query.strip():
            raise ValueError("Geocoding query must be nonempty.")
        self._wait_for_rate_limit()
        try:
            response = self._client.get("/search", params={"q": query, "format": "jsonv2", "limit": 1})
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise NominatimUnavailableError("Nominatim provider is unavailable.") from error
        try:
            payload = response.json()
        except ValueError as error:
            raise NominatimResponseError("Nominatim response is not valid JSON.") from error
        return self._parse(payload)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _wait_for_rate_limit(self) -> None:
        with self._rate_limit_lock:
            now = self._monotonic()
            delay = self._next_request_at - now
            if delay > 0:
                self._sleep(delay)
                now = self._monotonic()
            self._next_request_at = max(now, self._next_request_at) + 1.0

    @staticmethod
    def _parse(payload: Any) -> GeocodingResult | None:
        if not isinstance(payload, list):
            raise NominatimResponseError("Nominatim response must be a JSON array.")
        if not payload:
            return None
        item = payload[0]
        if not isinstance(item, dict):
            raise NominatimResponseError("Nominatim result must be a JSON object.")
        latitude = NominatimGeocoder._finite_float(item.get("lat"), "lat")
        longitude = NominatimGeocoder._finite_float(item.get("lon"), "lon")
        if not -90 <= latitude <= 90:
            raise NominatimResponseError("Nominatim result has an out-of-range latitude.")
        if not -180 <= longitude <= 180:
            raise NominatimResponseError("Nominatim result has an out-of-range longitude.")
        provider_key = item.get("place_id")
        resolved_query = item.get("display_name")
        if not isinstance(provider_key, (str, int)) or not str(provider_key).strip():
            raise NominatimResponseError("Nominatim result has no valid provider key.")
        if not isinstance(resolved_query, str) or not resolved_query.strip():
            raise NominatimResponseError("Nominatim result has no valid display name.")
        return GeocodingResult(latitude, longitude, resolved_query, str(provider_key))

    @staticmethod
    def _finite_float(value: Any, field: str) -> float:
        try:
            result = float(value)
        except (TypeError, ValueError) as error:
            raise NominatimResponseError(f"Nominatim result has no valid {field}.") from error
        if result != result or result in {float("inf"), float("-inf")}:
            raise NominatimResponseError(f"Nominatim result has no finite {field}.")
        return result
