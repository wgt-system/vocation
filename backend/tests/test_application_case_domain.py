from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from vocation.domain.application_cases import (
    ApplicationCaseConflictError,
    ApplicationCaseError,
    change_application_case_lifecycle,
    create_application_case,
    create_application_material,
    revise_application_material,
)

OCCURRED_AT = datetime(2026, 8, 13, 12, tzinfo=UTC)


def test_creation_starts_in_draft_with_initial_history_event() -> None:
    case = create_application_case("case-1", "opportunity-1", OCCURRED_AT)

    assert case.lifecycle == "draft"
    assert case.created_at == OCCURRED_AT
    assert case.updated_at == OCCURRED_AT
    assert len(case.lifecycle_events) == 1
    assert case.lifecycle_events[0].previous_status is None
    assert case.lifecycle_events[0].resulting_status == "draft"
    assert case.lifecycle_events[0].occurred_at == OCCURRED_AT


def test_lifecycle_change_appends_history_and_leaves_original_immutable() -> None:
    case = create_application_case("case-1", "opportunity-1", OCCURRED_AT)
    changed_at = OCCURRED_AT + timedelta(hours=1)

    changed = change_application_case_lifecycle(case, "ready", changed_at)

    assert case.lifecycle == "draft"
    assert len(case.lifecycle_events) == 1
    assert changed.lifecycle == "ready"
    assert changed.created_at == case.created_at
    assert changed.updated_at == changed_at
    assert len(changed.lifecycle_events) == 2
    assert changed.lifecycle_events[-1].previous_status == "draft"
    assert changed.lifecycle_events[-1].resulting_status == "ready"


def test_terminal_lifecycle_cannot_transition_further() -> None:
    case = create_application_case("case-1", "opportunity-1", OCCURRED_AT)
    terminal = change_application_case_lifecycle(case, "accepted", OCCURRED_AT)

    with pytest.raises(ApplicationCaseConflictError):
        change_application_case_lifecycle(terminal, "draft", OCCURRED_AT)


def test_same_state_and_unsupported_lifecycle_reject() -> None:
    case = create_application_case("case-1", "opportunity-1", OCCURRED_AT)

    with pytest.raises(ApplicationCaseConflictError):
        change_application_case_lifecycle(case, "draft", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        change_application_case_lifecycle(case, "unknown", OCCURRED_AT)


def test_material_creation_validates_kind_and_name_and_starts_revision_one() -> None:
    material = create_application_material("material-1", "case-1", "cv", "  Resume  ", OCCURRED_AT)

    assert material.kind == "cv"
    assert material.display_name == "Resume"
    assert material.revision == 1
    assert material.created_at == material.updated_at == OCCURRED_AT
    with pytest.raises(ApplicationCaseError):
        create_application_material("material-2", "case-1", "invalid", "Resume", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        create_application_material("material-2", "case-1", "cv", "   ", OCCURRED_AT)


def test_material_revision_preserves_identity_and_kind_and_increments_revision() -> None:
    material = create_application_material("material-1", "case-1", "cover_letter", "Letter", OCCURRED_AT)
    revised_at = OCCURRED_AT + timedelta(hours=2)

    revised = revise_application_material(material, display_name="  New Letter  ", occurred_at=revised_at)

    assert material.display_name == "Letter"
    assert material.revision == 1
    assert revised.id == material.id
    assert revised.application_case_id == material.application_case_id
    assert revised.kind == material.kind
    assert revised.created_at == material.created_at
    assert revised.display_name == "New Letter"
    assert revised.revision == 2
    assert revised.updated_at == revised_at


def test_invalid_or_blank_ids_and_blank_display_names_reject() -> None:
    with pytest.raises(ApplicationCaseError):
        create_application_case(" ", "opportunity-1", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        create_application_case("case-1", "", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        create_application_material("", "case-1", "other", "Name", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        create_application_material("material-1", " ", "other", "Name", OCCURRED_AT)
    with pytest.raises(ApplicationCaseError):
        create_application_material("material-1", "case-1", "other", " ", OCCURRED_AT)
