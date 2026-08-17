from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import pytest
from vocation.infrastructure.orientation_geocoder import (
    OrientationGeocoder,
    OrientationGeocoderResponseError,
    OrientationGeocoderUnavailableError,
)


def encode(payload) -> bytes:
    return json.dumps(payload).encode("utf-8")


def make_geocoder(handler):
    return OrientationGeocoder("http://orientation.test", transport=handler)


def test_successful_parsing_and_request_contract() -> None:
    requests: list[tuple[str, float]] = []

    def handler(url: str, timeout: float) -> bytes:
        requests.append((url, timeout))
        return encode(
            {
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
            }
        )

    result = make_geocoder(handler).geocode(" Berlin, Germany ")

    assert result is not None
    assert (result.latitude, result.longitude, result.provider_key, result.resolved_query) == (
        52.52,
        13.405,
        "photon:node:123",
        "Berlin, Deutschland",
    )
    parsed = urlsplit(requests[0][0])
    assert parsed.path == "/api/v1/places/search"
    assert parse_qs(parsed.query) == {"q": ["Berlin, Germany"], "limit": ["1"]}
    assert requests[0][1] == OrientationGeocoder.REQUEST_TIMEOUT_SECONDS


def test_no_result() -> None:
    assert make_geocoder(lambda _url, _timeout: encode({"places": []})).geocode("unknown") is None


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
        make_geocoder(lambda _url, _timeout: encode(payload)).geocode("query")


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(OrientationGeocoderResponseError):
        make_geocoder(lambda _url, _timeout: b"not-json").geocode("query")


def test_network_failure_is_deterministic() -> None:
    def handler(_url: str, _timeout: float) -> bytes:
        raise OSError("offline")

    with pytest.raises(OrientationGeocoderUnavailableError):
        make_geocoder(handler).geocode("query")


def test_transport_unavailable_failure_is_preserved() -> None:
    def handler(_url: str, _timeout: float) -> bytes:
        raise OrientationGeocoderUnavailableError("Orientation place search is unavailable.")

    with pytest.raises(OrientationGeocoderUnavailableError):
        make_geocoder(handler).geocode("query")


def test_blank_query_is_rejected_without_request() -> None:
    requests: list[str] = []

    def handler(url: str, _timeout: float) -> bytes:
        requests.append(url)
        return encode({"places": []})

    with pytest.raises(ValueError):
        make_geocoder(handler).geocode("   ")

    assert requests == []
