from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from tests.test_migrations import insert_duplicate_case, migrate, seed_v020_data
from vocation.domain.groups import OpportunityGroup
from vocation.infrastructure.database import Database
from vocation.infrastructure.group_repository import (
    OpportunityGroupMembershipError,
    OpportunityGroupNotFoundError,
    OpportunityGroupValidationError,
    OpportunityNotFoundError,
    SqlAlchemyOpportunityGroupRepository,
)


def make_repository(database: Path) -> tuple[Database, SqlAlchemyOpportunityGroupRepository]:
    db = Database(f"sqlite:///{database.as_posix()}")
    return db, SqlAlchemyOpportunityGroupRepository(db.session_factory)


def test_0009_migration_and_restart_preserve_existing_state(tmp_path: Path) -> None:
    database = tmp_path / "groups-upgrade.db"
    migrate(database, "0008")
    seed_v020_data(database)
    insert_duplicate_case(database)
    migrate(database, "head")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert {"opportunity_groups", "opportunity_group_memberships"}.issubset(inspector.get_table_names())
    db, repository = make_repository(database)
    repository.create(OpportunityGroup("group-1", "Wave", None, "application_wave"))
    repository.add_opportunity("group-1", "opportunity-1")
    repository.add_opportunity("group-1", "opportunity-2")
    db.dispose()

    restarted, restarted_repository = make_repository(database)
    group = restarted_repository.get("group-1")
    assert group is not None
    assert [membership.opportunity_id for membership in group.memberships] == ["opportunity-1", "opportunity-2"]
    with restarted.engine.connect() as connection:
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases WHERE id = 'case-1'")) == 1
        assert (
            connection.scalar(text("SELECT source_reference_id FROM duplicate_case_source_references WHERE duplicate_case_id = 'case-1'"))
            == "ref-1"
        )
    restarted.dispose()


def test_group_lifecycle_memberships_and_reorder(tmp_path: Path) -> None:
    database = tmp_path / "groups.db"
    migrate(database, "head")
    seed_v020_data(database)
    db, repository = make_repository(database)

    created = repository.create(OpportunityGroup("group-1", "Initial", "Description", "general"))
    assert created.memberships == ()
    edited = repository.edit("group-1", name="Edited", description=None, group_type="application_wave")
    assert (edited.name, edited.description, edited.group_type) == ("Edited", None, "application_wave")
    repository.add_opportunity("group-1", "opportunity-1")
    repository.add_opportunity("group-1", "opportunity-2")
    with pytest.raises(OpportunityGroupMembershipError):
        repository.add_opportunity("group-1", "opportunity-1")

    repository.remove_opportunity("group-1", "opportunity-1")
    assert [(item.opportunity_id, item.position) for item in repository.get("group-1").memberships] == [("opportunity-2", 0)]  # type: ignore[union-attr]
    repository.add_opportunity("group-1", "opportunity-1")
    repository.reorder("group-1", ["opportunity-1", "opportunity-2"])
    assert [(item.opportunity_id, item.position) for item in repository.get("group-1").memberships] == [
        ("opportunity-1", 0),
        ("opportunity-2", 1),
    ]  # type: ignore[union-attr]
    with pytest.raises(OpportunityGroupMembershipError):
        repository.reorder("group-1", ["opportunity-1", "opportunity-1"])
    with pytest.raises(OpportunityGroupMembershipError):
        repository.reorder("group-1", ["opportunity-1"])

    repository.delete("group-1")
    assert repository.get("group-1") is None
    with db.engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_group_memberships")) == 0
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities")) == 2
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions")) == 1
    db.dispose()


def test_group_operations_have_deterministic_errors_and_model_constraints(tmp_path: Path) -> None:
    database = tmp_path / "group-errors.db"
    migrate(database, "head")
    seed_v020_data(database)
    db, repository = make_repository(database)

    with pytest.raises(OpportunityGroupValidationError):
        repository.create(OpportunityGroup("group-1", "   ", None, "general"))
    with pytest.raises(OpportunityGroupValidationError):
        repository.create(OpportunityGroup("group-1", "Name", None, "invalid"))  # type: ignore[arg-type]
    with pytest.raises(OpportunityGroupNotFoundError):
        repository.edit("missing", name="Name", description=None, group_type="general")
    with pytest.raises(OpportunityGroupNotFoundError):
        repository.add_opportunity("missing", "missing-opportunity")

    repository.create(OpportunityGroup("group-1", "Name", None, "general"))
    with pytest.raises(OpportunityNotFoundError):
        repository.add_opportunity("group-1", "missing-opportunity")
    with pytest.raises(OpportunityGroupNotFoundError):
        repository.remove_opportunity("missing", "opportunity-1")

    with db.engine.begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(text("INSERT INTO opportunity_groups (id, name, group_type) VALUES ('group-2', '', 'general')"))
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO opportunity_group_memberships (group_id, opportunity_id, position) VALUES ('group-1', 'opportunity-1', -1)"
                )
            )
    db.dispose()


def test_0009_downgrade_removes_only_group_tables(tmp_path: Path) -> None:
    database = tmp_path / "groups-downgrade.db"
    migrate(database, "head")
    seed_v020_data(database)
    insert_duplicate_case(database)
    db, repository = make_repository(database)
    repository.create(OpportunityGroup("group-1", "Name", None, "general"))
    repository.add_opportunity("group-1", "opportunity-1")
    db.dispose()

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0008")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "opportunity_groups" not in inspector.get_table_names()
    assert "opportunity_group_memberships" not in inspector.get_table_names()
    with create_engine(f"sqlite:///{database.as_posix()}").connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities")) == 2
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases WHERE id = 'case-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
