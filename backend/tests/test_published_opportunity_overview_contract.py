from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "published-opportunity-overview-v1.schema.json"
EXAMPLE = ROOT / "examples" / "publication" / "opportunity-overview-v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_canonical_example_validates(validator: Draft202012Validator) -> None:
    assert not list(validator.iter_errors(load(EXAMPLE)))


def test_empty_market_is_valid(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["opportunities"] = []
    assert not list(validator.iter_errors(artifact))


@pytest.mark.parametrize("property_name", ["capability", "contract_version", "publication", "opportunities"])
def test_missing_top_level_required_property_rejects(validator: Draft202012Validator, property_name: str) -> None:
    artifact = load(EXAMPLE)
    artifact.pop(property_name)
    assert list(validator.iter_errors(artifact))


def test_unknown_property_rejects_at_each_object_level(validator: Draft202012Validator) -> None:
    cases = []
    top = load(EXAMPLE)
    top["unknown"] = True
    cases.append(top)
    publication = load(EXAMPLE)
    publication["publication"]["unknown"] = True
    cases.append(publication)
    company = load(EXAMPLE)
    company["opportunities"][0]["company"]["unknown"] = True
    cases.append(company)
    location = load(EXAMPLE)
    location["opportunities"][0]["work_locations"][0]["unknown"] = True
    cases.append(location)
    opportunity = load(EXAMPLE)
    opportunity["opportunities"][0]["unknown"] = True
    cases.append(opportunity)
    for artifact in cases:
        assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    ("property_name", "value"),
    [("capability", "other.capability"), ("contract_version", "2.0")],
)
def test_capability_and_version_are_frozen(validator: Draft202012Validator, property_name: str, value: str) -> None:
    artifact = load(EXAMPLE)
    artifact[property_name] = value
    assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("country_code", "de"),
        ("precision", "exact"),
        ("tracking_status", "interesting"),
        ("import_id", "private"),
        ("availability", "available"),
        ("url", "https://example.invalid"),
    ],
)
def test_invalid_or_forbidden_fields_reject(validator: Draft202012Validator, field: str, value: str) -> None:
    artifact = load(EXAMPLE)
    if field in {"country_code", "precision"}:
        artifact["opportunities"][0]["work_locations"][0][field] = value
    else:
        artifact["opportunities"][0][field] = value
    assert list(validator.iter_errors(artifact))


def test_refs_are_opaque_bounded_strings(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["publication"]["publication_ref"] = ""
    assert list(validator.iter_errors(artifact))
    artifact = load(EXAMPLE)
    artifact["opportunities"][0]["opportunity_ref"] = "x" * 201
    assert list(validator.iter_errors(artifact))
