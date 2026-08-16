from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "published-map-projection-v1.schema.json"
EXAMPLE = ROOT / "examples" / "publication" / "published-map-projection-v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_canonical_example_validates(validator: Draft202012Validator) -> None:
    assert not list(validator.iter_errors(load(EXAMPLE)))


def test_empty_features_is_valid(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["features"] = []
    assert not list(validator.iter_errors(artifact))


@pytest.mark.parametrize("field", ["capability", "contract_version", "publication", "features"])
def test_missing_required_property_rejects(validator: Draft202012Validator, field: str) -> None:
    artifact = load(EXAMPLE)
    artifact.pop(field)
    assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    ("field", "value"),
    [("capability", "vocation.other"), ("contract_version", "2.0")],
)
def test_capability_and_version_are_frozen(validator: Draft202012Validator, field: str, value: str) -> None:
    artifact = load(EXAMPLE)
    artifact[field] = value
    assert list(validator.iter_errors(artifact))


def test_unknown_property_rejects_at_each_object_level(validator: Draft202012Validator) -> None:
    cases = []
    top = load(EXAMPLE)
    top["unknown"] = True
    cases.append(top)
    publication = load(EXAMPLE)
    publication["publication"]["unknown"] = True
    cases.append(publication)
    feature = load(EXAMPLE)
    feature["features"][0]["unknown"] = True
    cases.append(feature)
    company = load(EXAMPLE)
    company["features"][0]["company"]["unknown"] = True
    cases.append(company)
    location = load(EXAMPLE)
    location["features"][0]["work_location"]["unknown"] = True
    cases.append(location)
    coordinates = load(EXAMPLE)
    coordinates["features"][0]["coordinates"]["unknown"] = True
    cases.append(coordinates)
    for artifact in cases:
        assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", 91),
        ("longitude", -181),
        ("precision", "exact"),
        ("tracking_status", "interesting"),
        ("url", "https://example.invalid"),
        ("availability", "available"),
    ],
)
def test_invalid_or_forbidden_fields_reject(validator: Draft202012Validator, field: str, value: object) -> None:
    artifact = load(EXAMPLE)
    if field in {"latitude", "longitude"}:
        artifact["features"][0]["coordinates"][field] = value
    elif field == "precision":
        artifact["features"][0]["work_location"][field] = value
    else:
        artifact["features"][0][field] = value
    assert list(validator.iter_errors(artifact))


def test_refs_are_opaque_bounded_strings(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["publication"]["publication_ref"] = ""
    assert list(validator.iter_errors(artifact))
    artifact = load(EXAMPLE)
    artifact["features"][0]["feature_ref"] = "x" * 201
    assert list(validator.iter_errors(artifact))
