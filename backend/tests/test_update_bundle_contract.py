from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
UPDATE_SCHEMA = ROOT / "schemas" / "research-update-bundle-v2.schema.json"
V1_SCHEMA = ROOT / "schemas" / "research-bundle-v1.schema.json"
UPDATE_EXAMPLES = ROOT / "examples" / "updates"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def update_validator() -> Draft202012Validator:
    schema = load(UPDATE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_research_bundle_v1_valid_example_remains_valid_and_initial_only() -> None:
    validator = Draft202012Validator(load(V1_SCHEMA), format_checker=FormatChecker())
    initial = load(ROOT / "examples" / "imports" / "initial-valid.json")
    assert not list(validator.iter_errors(initial))
    update = copy.deepcopy(initial)
    update["research_scope"]["type"] = "full_update"
    assert list(validator.iter_errors(update))


@pytest.mark.parametrize(
    "name", ["full-update-valid.json", "company-update-valid.json", "opportunity-update-valid.json", "gap-filling-valid.json"]
)
def test_each_update_scope_example_validates(update_validator: Draft202012Validator, name: str) -> None:
    bundle = load(UPDATE_EXAMPLES / name)
    assert not list(update_validator.iter_errors(bundle))


@pytest.mark.parametrize("name", ["invalid-protected-state.json", "invalid-structure.json", "invalid-gap-new-entity.json"])
def test_invalid_update_examples_are_rejected(update_validator: Draft202012Validator, name: str) -> None:
    assert list(update_validator.iter_errors(load(UPDATE_EXAMPLES / name)))


def test_known_subjects_are_opaque_and_new_subjects_have_creation_fields(update_validator: Draft202012Validator) -> None:
    bundle = load(UPDATE_EXAMPLES / "company-update-valid.json")
    assert "correlation_ref" in bundle["companies"][0]
    assert "canonical_name" not in bundle["companies"][0]
    assert "correlation_ref" not in bundle["opportunities"][0]
    assert "canonical_title" in bundle["opportunities"][0]
    assert not list(update_validator.iter_errors(bundle))


def test_possible_duplicate_is_evidence_only_and_gap_filling_has_none(update_validator: Draft202012Validator) -> None:
    full = load(UPDATE_EXAMPLES / "full-update-valid.json")
    duplicate = full["possible_duplicates"][0]
    assert duplicate["subject_type"] in {"opportunity", "posting"}
    assert duplicate["left_subject_id"] != duplicate["right_subject_id"]
    gap = load(UPDATE_EXAMPLES / "gap-filling-valid.json")
    assert gap["possible_duplicates"] == []
    assert not list(update_validator.iter_errors(full))
    assert not list(update_validator.iter_errors(gap))
