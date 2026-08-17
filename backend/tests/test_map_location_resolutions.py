from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from tests.test_migrations import migrate, seed_v020_data
from vocation.domain.map_locations import MapLocationResolution
from vocation.infrastructure.database import Database
from vocation.infrastructure.map_location_repository import (
    MapLocationResolutionValidationError,
    SqlAlchemyMapLocationResolutionRepository,
    WorkLocationNotFoundError,
)

RESOLVED_AT = datetime(2026, 8, 9, 12, 0)


def seed_work_locations(database: Path) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        for location_id, label in (("location-1", "Berlin"), ("location-2", "Munich")):
            connection.execute(
                text(
                    "INSERT INTO work_locations "
                    "(id, opportunity_id, label, city, region, country_code, precision, source_reference_id, observed_at) "
                    "VALUES (:id, 'opportunity-1', :label, :label, 'BE', 'DE', 'city', 'ref-1', '2025-01-01')"
                ),
                {"id": location_id, "label": label},
            )


def make_repository(database: Path) -> tuple[Database, SqlAlchemyMapLocationResolutionRepository]:
    db = Database(f"sqlite:///{database.as_posix()}")
    return db, SqlAlchemyMapLocationResolutionRepository(db.session_factory)


def resolution(work_location_id: str, *, source: str = "manual", provider_key: str | None = None) -> MapLocationResolution:
    return MapLocationResolution(
        work_location_id=work_location_id,
        latitude=52.52,
        longitude=13.405,
        resolution_source=source,  # type: ignore[arg-type]
        provider_key=provider_key,
        resolved_at=RESOLVED_AT,
        resolved_query="Berlin, Germany",
    )


def test_0010_fresh_upgrade_restart_and_downgrade(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh.db"
    migrated = tmp_path / "migrated.db"
    migrate(fresh, "head")
    assert "map_location_resolutions" in inspect(create_engine(f"sqlite:///{fresh.as_posix()}")).get_table_names()

    migrate(migrated, "0009")
    seed_v020_data(migrated)
    seed_work_locations(migrated)
    migrate(migrated, "head")
    db, repository = make_repository(migrated)
    repository.set(resolution("location-1"))
    db.dispose()

    restarted, restarted_repository = make_repository(migrated)
    assert restarted_repository.get("location-1") == resolution("location-1")
    with restarted.engine.connect() as connection:
        assert connection.scalar(text("SELECT city FROM work_locations WHERE id = 'location-1'")) == "Berlin"

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{migrated.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0009")
    inspector = inspect(create_engine(f"sqlite:///{migrated.as_posix()}"))
    assert "map_location_resolutions" not in inspector.get_table_names()
    assert "work_locations" in inspector.get_table_names()
    restarted.dispose()


def test_resolution_create_replace_delete_and_list_are_isolated(tmp_path: Path) -> None:
    database = tmp_path / "resolution.db"
    migrate(database, "head")
    seed_v020_data(database)
    seed_work_locations(database)
    db, repository = make_repository(database)

    original_location = repository.get("location-1")
    assert original_location is None
    repository.set(resolution("location-1"))
    repository.set(resolution("location-2"))
    replaced = MapLocationResolution("location-1", 48.137, 11.575, "geocoder", "provider-x", RESOLVED_AT, "Munich, Germany")
    assert repository.set(replaced) == replaced
    assert repository.list(["location-2", "location-1", "location-1"]) == [replaced, resolution("location-2")]

    repository.delete("location-1")
    assert repository.get("location-1") is None
    with db.engine.connect() as connection:
        assert connection.scalar(text("SELECT city FROM work_locations WHERE id = 'location-1'")) == "Berlin"
        assert connection.scalar(text("SELECT COUNT(*) FROM map_location_resolutions")) == 1
    db.dispose()


@pytest.mark.parametrize(
    "candidate",
    [
        MapLocationResolution("location-1", -90.01, 0, "manual", None, RESOLVED_AT, "query"),
        MapLocationResolution("location-1", 0, 180.01, "manual", None, RESOLVED_AT, "query"),
        MapLocationResolution("location-1", 0, 0, "invalid", None, RESOLVED_AT, "query"),  # type: ignore[arg-type]
        MapLocationResolution("location-1", 0, 0, "manual", "provider", RESOLVED_AT, "query"),
        MapLocationResolution("location-1", 0, 0, "geocoder", None, RESOLVED_AT, "query"),
        MapLocationResolution("location-1", 0, 0, "geocoder", "   ", RESOLVED_AT, "query"),
        MapLocationResolution("location-1", 0, 0, "manual", None, RESOLVED_AT, "   "),
    ],
)
def test_resolution_validation_and_unknown_work_location(tmp_path: Path, candidate: MapLocationResolution) -> None:
    database = tmp_path / "resolution-errors.db"
    migrate(database, "head")
    seed_v020_data(database)
    seed_work_locations(database)
    db, repository = make_repository(database)

    with pytest.raises(MapLocationResolutionValidationError):
        repository.set(candidate)
    with pytest.raises(WorkLocationNotFoundError):
        repository.set(resolution("missing"))
    with pytest.raises(WorkLocationNotFoundError):
        repository.get("missing")
    with pytest.raises(WorkLocationNotFoundError):
        repository.list(["location-1", "missing"])

    with db.engine.begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO map_location_resolutions "
                    "(work_location_id, latitude, longitude, resolution_source, resolved_at, resolved_query) "
                    "VALUES ('location-1', 91, 0, 'manual', '2026-08-09', 'query')"
                )
            )
    db.dispose()
