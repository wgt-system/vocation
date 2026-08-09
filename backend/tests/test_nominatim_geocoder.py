from __future__ import annotations

import httpx
import pytest
from vocation.infrastructure.nominatim_geocoder import (
    NominatimGeocoder,
    NominatimResponseError,
    NominatimUnavailableError,
)


def make_geocoder(handler, *, clock=None, sleep=None):
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://nominatim.test")
    return NominatimGeocoder("https://nominatim.test", client=client, monotonic=clock or (lambda: 10.0), sleep=sleep or (lambda _: None))


def test_successful_parsing_and_request_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[{"lat": "52.5200", "lon": "13.4050", "place_id": 123, "display_name": "Berlin, Deutschland"}])

    result = make_geocoder(handler).geocode("Berlin, Germany")

    assert result is not None
    assert (result.latitude, result.longitude, result.provider_key, result.resolved_query) == (52.52, 13.405, "123", "Berlin, Deutschland")
    assert requests[0].url.path == "/search"
    assert dict(requests[0].url.params) == {"q": "Berlin, Germany", "format": "jsonv2", "limit": "1"}
    assert requests[0].headers["user-agent"].startswith("Vocation/")


def test_no_result() -> None:
    assert make_geocoder(lambda _: httpx.Response(200, json=[])).geocode("unknown") is None


@pytest.mark.parametrize(
    "payload",
    [None, [{}], [{"lat": "not-a-number", "lon": "1", "place_id": "x", "display_name": "Place"}]],
)
def test_malformed_response_is_rejected(payload) -> None:
    with pytest.raises(NominatimResponseError):
        make_geocoder(lambda _: httpx.Response(200, json=payload)).geocode("query")


def test_network_failure_is_deterministic() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline")

    with pytest.raises(NominatimUnavailableError):
        make_geocoder(handler).geocode("query")


def test_rate_limit_uses_injected_clock_and_sleep() -> None:
    current = [0.0]
    sleeps: list[float] = []

    def clock() -> float:
        return current[0]

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        current[0] += seconds

    geocoder = make_geocoder(lambda _: httpx.Response(200, json=[]), clock=clock, sleep=sleep)
    geocoder.geocode("one")
    geocoder.geocode("two")

    assert sleeps == [1.0]
