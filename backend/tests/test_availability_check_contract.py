from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "availability-check-bundle-v1.schema.json"
EXAMPLE = ROOT / "examples" / "imports" / "availability-check-valid.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_canonical_example_validates(validator: Draft202012Validator) -> None:
    assert not list(validator.iter_errors(load(EXAMPLE)))


@pytest.mark.parametrize(
    ("field", "value"),
    [("bundle_kind", "research"), ("bundle_version", "2.0")],
)
def test_kind_and_version_are_frozen(validator: Draft202012Validator, field: str, value: str) -> None:
    artifact = load(EXAMPLE)
    artifact[field] = value
    assert list(validator.iter_errors(artifact))


def test_unknown_properties_reject_at_top_and_observation_levels(
    validator: Draft202012Validator,
) -> None:
    artifact = load(EXAMPLE)
    artifact["unknown"] = True
    assert list(validator.iter_errors(artifact))
    artifact = load(EXAMPLE)
    artifact["observations"][0]["unknown"] = True
    assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    "field",
    [
        "bundle_kind",
        "bundle_version",
        "bundle_id",
        "generated_at",
        "prompt_context_ref",
        "research_scope",
        "observations",
        "warnings",
    ],
)
def test_missing_required_fields_rejects(validator: Draft202012Validator, field: str) -> None:
    artifact = load(EXAMPLE)
    artifact.pop(field)
    assert list(validator.iter_errors(artifact))


def test_invalid_result_rejects(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["observations"][0]["result"] = "unknown"
    assert list(validator.iter_errors(artifact))


def test_empty_selected_refs_rejects(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["research_scope"]["selected_correlation_refs"] = []
    assert list(validator.iter_errors(artifact))


def test_duplicate_selected_refs_rejects(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    refs = artifact["research_scope"]["selected_correlation_refs"]
    refs.append(refs[0])
    assert list(validator.iter_errors(artifact))


def test_empty_observations_rejects(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["observations"] = []
    assert list(validator.iter_errors(artifact))


@pytest.mark.parametrize(
    "field",
    [
        "posting_id",
        "company_id",
        "opportunity_id",
        "internal_id",
        "tracking_status",
        "url",
        "assessment",
        "mutation",
    ],
)
def test_internal_and_mutation_fields_reject(validator: Draft202012Validator, field: str) -> None:
    artifact = load(EXAMPLE)
    artifact["observations"][0][field] = "forbidden"
    assert list(validator.iter_errors(artifact))


def test_opaque_refs_are_bounded_strings(validator: Draft202012Validator) -> None:
    artifact = load(EXAMPLE)
    artifact["prompt_context_ref"] = ""
    assert list(validator.iter_errors(artifact))
    artifact = copy.deepcopy(load(EXAMPLE))
    artifact["research_scope"]["selected_correlation_refs"][0] = "x" * 201
    assert list(validator.iter_errors(artifact))
