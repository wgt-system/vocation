from __future__ import annotations

import httpx
import pytest
from vocation.infrastructure.orientation_geocoder import (
    OrientationGeocoder,
    OrientationGeocoderResponseError,
    OrientationGeocoderUnavailableError,
)


def make_geocoder(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://orientation.test")
    return OrientationGeocoder("http://orientation.test", client=client)


def test_successful_parsing_and_request_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "places": [
                    {
                        "providerReference": "photon:node:123",
                        "displayLabel": "Berlin, Deutschland",
                        "coordinate": {"longitude": 13.405, "latitude": 52.52},
                        "extent": None,
                        "kind": None,
                        "address": {
                            "name": "Berlin",
                            "street": None,
                            "houseNumber": None,
                            "postcode": None,
                            "city": "Berlin",
                            "county": None,
                            "state": "Berlin",
                            "country": "Deutschland",
                            "countryCode": "de",
                        },
                    }
                ]
            },
        )

    result = make_geocoder(handler).geocode(" Berlin, Germany ")

    assert result is not None
    assert (result.latitude, result.longitude, result.provider_key, result.resolved_query) == (
        52.52,
        13.405,
        "photon:node:123",
        "Berlin, Deutschland",
    )
    assert requests[0].url.path == "/api/v1/places/search"
    assert dict(requests[0].url.params) == {"q": "Berlin, Germany", "limit": "1"}


def test_no_result() -> None:
    assert make_geocoder(lambda _: httpx.Response(200, json={"places": []})).geocode("unknown") is None


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"places": [None]},
        {"places": [{}]},
        {
            "places": [
                {
                    "providerReference": "ref",
                    "displayLabel": "Place",
                    "coordinate": {"longitude": 181, "latitude": 52},
                }
            ]
        },
    ],
)
def test_malformed_response_is_rejected(payload) -> None:
    with pytest.raises(OrientationGeocoderResponseError):
        make_geocoder(lambda _: httpx.Response(200, json=payload)).geocode("query")


def test_network_failure_is_deterministic() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline")

    with pytest.raises(OrientationGeocoderUnavailableError):
        make_geocoder(handler).geocode("query")


def test_non_success_response_is_unavailable() -> None:
    with pytest.raises(OrientationGeocoderUnavailableError):
        make_geocoder(lambda _: httpx.Response(503, json={"code": "provider.unavailable"})).geocode("query")


def test_blank_query_is_rejected_without_request() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"places": []})

    with pytest.raises(ValueError):
        make_geocoder(handler).geocode("   ")

    assert requests == []
