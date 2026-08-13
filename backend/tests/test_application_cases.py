from __future__ import annotations

from datetime import UTC, datetime, timedelta
from itertools import chain, count, repeat
from pathlib import Path

import pytest
from sqlalchemy import text
from tests.test_migrations import migrate, seed_v020_data
from vocation.application.application_cases import (
    ApplicationCaseNotFoundError,
    ApplicationCaseService,
    ApplicationMaterialNotFoundError,
)
from vocation.domain.application_cases import ApplicationCaseConflictError as ServiceConflictError
from vocation.infrastructure.application_case_repository import (
    OpportunityNotFoundError,
    SqlAlchemyApplicationCaseRepository,
)
from vocation.infrastructure.database import Database

BASE_TIME = datetime(2026, 8, 13, 12, tzinfo=UTC)


def make_service(database: Path, *, times: list[datetime] | None = None):
    migrate(database, "head")
    seed_v020_data(database)
    db = Database(f"sqlite:///{database.as_posix()}")
    repository = SqlAlchemyApplicationCaseRepository(db.session_factory)
    values = chain(times or (), repeat((times or [BASE_TIME])[-1]))
    ref_counter = count(1)
    service = ApplicationCaseService(
        repository,
        ref_factory=lambda: f"ref-{next(ref_counter)}",
        clock=lambda: next(values),
    )
    return db, repository, service


def test_create_persists_draft_case_and_initial_event(tmp_path: Path) -> None:
    db, repository, service = make_service(tmp_path / "create.db")

    case = service.create_case("opportunity-1")

    assert case.id == "ref-1"
    assert case.lifecycle == "draft"
    assert len(case.lifecycle_events) == 1
    assert case.lifecycle_events[0].previous_status is None
    assert case.lifecycle_events[0].resulting_status == "draft"
    with db.engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM application_case_lifecycle_events")) == 1
    assert repository.get(case.id) == case
    db.dispose()


def test_second_active_case_is_rejected_but_terminal_history_allows_new_case(tmp_path: Path) -> None:
    db, _repository, service = make_service(
        tmp_path / "active.db",
        times=[BASE_TIME, BASE_TIME + timedelta(hours=1), BASE_TIME + timedelta(hours=2), BASE_TIME + timedelta(hours=3)],
    )

    first = service.create_case("opportunity-1")
    with pytest.raises(ServiceConflictError):
        service.create_case("opportunity-1")

    service.change_lifecycle(first.id, "accepted")
    second = service.create_case("opportunity-1")

    assert second.lifecycle == "draft"
    assert len(service.list_for_opportunity("opportunity-1")) == 2
    db.dispose()


def test_lifecycle_change_persists_append_only_ordered_history(tmp_path: Path) -> None:
    db, _repository, service = make_service(tmp_path / "lifecycle.db", times=[BASE_TIME, BASE_TIME + timedelta(hours=1)])

    original = service.create_case("opportunity-1")
    changed = service.change_lifecycle(original.id, "ready")
    loaded = service.get(original.id)

    assert loaded is not None
    assert loaded.lifecycle == "ready"
    assert original.lifecycle == "draft"
    assert [event.resulting_status for event in loaded.lifecycle_events] == ["draft", "ready"]
    assert loaded.lifecycle_events[1].previous_status == "draft"
    with db.engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT sequence, resulting_status FROM application_case_lifecycle_events "
                "WHERE application_case_id = :case_id ORDER BY sequence"
            ),
            {"case_id": original.id},
        ).all()
    assert rows == [(1, "draft"), (2, "ready")]
    assert changed == loaded
    db.dispose()


def test_terminal_and_same_state_conflicts_remain_domain_enforced(tmp_path: Path) -> None:
    db, _repository, service = make_service(
        tmp_path / "conflicts.db", times=[BASE_TIME, BASE_TIME + timedelta(hours=1), BASE_TIME + timedelta(hours=2)]
    )

    case = service.create_case("opportunity-1")
    with pytest.raises(ServiceConflictError):
        service.change_lifecycle(case.id, "draft")
    terminal = service.change_lifecycle(case.id, "rejected")
    with pytest.raises(ServiceConflictError):
        service.change_lifecycle(terminal.id, "ready")
    db.dispose()


def test_material_creation_and_revision_are_append_only(tmp_path: Path) -> None:
    db, _repository, service = make_service(
        tmp_path / "materials.db", times=[BASE_TIME, BASE_TIME + timedelta(hours=1), BASE_TIME + timedelta(hours=2)]
    )

    case = service.create_case("opportunity-1")
    material = service.create_material(case.id, "cv", "  Resume  ")
    revised = service.revise_material(material.id, "  Resume final  ")

    assert material.display_name == "Resume"
    assert revised.display_name == "Resume final"
    assert revised.revision == 2
    assert revised.id == material.id
    assert revised.kind == material.kind
    assert revised.created_at == material.created_at
    assert service.get(case.id) is not None
    assert service.list_materials(case.id) == [revised]
    with db.engine.connect() as connection:
        rows = connection.execute(
            text("SELECT revision, display_name FROM application_material_revisions WHERE material_id = :material_id ORDER BY revision"),
            {"material_id": material.id},
        ).all()
    assert rows == [(1, "Resume"), (2, "Resume final")]
    db.dispose()


def test_ordering_and_not_found_behavior(tmp_path: Path) -> None:
    db, _repository, service = make_service(tmp_path / "lookup.db", times=[BASE_TIME, BASE_TIME, BASE_TIME])

    first = service.create_case("opportunity-1")
    service.change_lifecycle(first.id, "accepted")
    second = service.create_case("opportunity-1")
    service.create_material(second.id, "other", "Notes")

    assert [case.id for case in service.list_for_opportunity("opportunity-1")] == [first.id, second.id]
    material = service.list_materials(second.id)[0]
    assert [item.id for item in service.list_materials(second.id)] == [material.id]
    assert service.get("missing") is None
    with pytest.raises(ApplicationCaseNotFoundError):
        service.change_lifecycle("missing", "ready")
    with pytest.raises(ApplicationCaseNotFoundError):
        service.create_material("missing", "cv", "Resume")
    with pytest.raises(ApplicationMaterialNotFoundError):
        service.revise_material("missing", "Resume")
    with pytest.raises(OpportunityNotFoundError):
        service.list_for_opportunity("missing")
    db.dispose()


def test_application_case_operations_do_not_change_tracking_status(tmp_path: Path) -> None:
    db, _repository, service = make_service(
        tmp_path / "tracking.db",
        times=[BASE_TIME, BASE_TIME + timedelta(hours=1), BASE_TIME + timedelta(hours=2), BASE_TIME + timedelta(hours=3)],
    )

    case = service.create_case("opportunity-1")
    service.change_lifecycle(case.id, "ready")
    material = service.create_material(case.id, "cover_letter", "Letter")
    service.revise_material(material.id, "Letter final")

    with db.engine.connect() as connection:
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
    db.dispose()
