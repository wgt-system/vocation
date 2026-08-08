from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def migrate(database: Path, revision: str) -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.upgrade(config, revision)


def schema(database: Path) -> dict:
    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    tables = {"opportunities", "personal_assessments", "opportunity_decisions"}
    result = {}
    for table in sorted(tables):
        result[table] = {
            "columns": [
                (column["name"], str(column["type"]), column["nullable"], str(column.get("default")))
                for column in inspector.get_columns(table)
            ],
            "foreign_keys": sorted(
                (
                    foreign_key["constrained_columns"],
                    foreign_key["referred_table"],
                    foreign_key["referred_columns"],
                    foreign_key.get("options", {}),
                )
                for foreign_key in inspector.get_foreign_keys(table)
            ),
            "indexes": sorted((index["name"], tuple(index["column_names"]), index["unique"]) for index in inspector.get_indexes(table)),
            "checks": sorted((check["name"], check["sqltext"]) for check in inspector.get_check_constraints(table)),
        }
    return result


def seed_v010_data(database: Path) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text("""
            INSERT INTO research_imports (id, status, created_at, counts_json, warnings_json)
            VALUES ('import-1', 'applied', '2025-01-01 00:00:00', '{}', '[]')
        """)
        )
        connection.execute(
            text("""
            INSERT INTO sources (id, import_id, bundle_local_id, name, source_type)
            VALUES ('source-1', 'import-1', 'source', 'Example', 'job_board')
        """)
        )
        connection.execute(
            text("""
            INSERT INTO source_references (id, import_id, bundle_local_id, source_id, url, normalized_url, observed_at)
            VALUES ('ref-1', 'import-1', 'ref', 'source-1', 'https://example.test/job', 'https://example.test/job', '2025-01-01 00:00:00')
        """)
        )
        connection.execute(
            text("""
            INSERT INTO companies (id, import_id, bundle_local_id, canonical_name, alternative_names_json, source_reference_id, observed_at)
            VALUES ('company-1', 'import-1', 'company', 'Example GmbH', '[]', 'ref-1', '2025-01-01 00:00:00')
        """)
        )
        connection.execute(
            text("""
            INSERT INTO opportunities (id, import_id, bundle_local_id, company_id, canonical_title, source_reference_id, observed_at)
            VALUES ('opportunity-1', 'import-1', 'opportunity', 'company-1', 'Junior Engineer', 'ref-1', '2025-01-01 00:00:00')
        """)
        )


def test_empty_and_v010_upgrade_produce_equivalent_triage_schema(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh.db"
    released = tmp_path / "released.db"
    migrate(fresh, "head")
    migrate(released, "0002")
    seed_v010_data(released)
    migrate(released, "head")

    assert schema(fresh) == schema(released)
    engine = create_engine(f"sqlite:///{released.as_posix()}")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT canonical_title FROM opportunities WHERE id = 'opportunity-1'")) == "Junior Engineer"


def test_triage_head_downgrades_to_0002(tmp_path: Path) -> None:
    database = tmp_path / "downgrade.db"
    migrate(database, "head")
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0002")
    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "personal_assessments" not in inspector.get_table_names()
    assert "opportunity_decisions" not in inspector.get_table_names()
    assert "tracking_status" not in {column["name"] for column in inspector.get_columns("opportunities")}
