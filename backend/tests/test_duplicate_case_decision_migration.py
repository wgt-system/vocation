from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError


def migrate(database: Path, revision: str) -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.upgrade(config, revision)


def seed_duplicate_case(database: Path) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO research_imports (id, status, created_at, counts_json, warnings_json) "
                "VALUES ('import-1', 'applied', '2026-08-17', '{}', '[]')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO sources (id, import_id, bundle_local_id, name, source_type) "
                "VALUES ('source-1', 'import-1', 'source-1', 'Example', 'job_board')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO source_references "
                "(id, import_id, bundle_local_id, source_id, url, normalized_url, observed_at) "
                "VALUES ('ref-1', 'import-1', 'ref-1', 'source-1', 'https://example.test/one', "
                "'https://example.test/one', '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO companies "
                "(id, import_id, bundle_local_id, canonical_name, alternative_names_json, source_reference_id, observed_at) "
                "VALUES ('company-1', 'import-1', 'company-1', 'Example GmbH', '[]', 'ref-1', '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO opportunities "
                "(id, import_id, bundle_local_id, company_id, canonical_title, source_reference_id, observed_at) "
                "VALUES ('opportunity-1', 'import-1', 'opportunity-1', 'company-1', 'Role One', 'ref-1', '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO opportunities "
                "(id, import_id, bundle_local_id, company_id, canonical_title, source_reference_id, observed_at) "
                "VALUES ('opportunity-2', 'import-1', 'opportunity-2', 'company-1', 'Role Two', 'ref-1', '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO duplicate_cases "
                "(id, research_import_id, subject_type, left_subject_id, right_subject_id, evidence_summary, confidence, created_at) "
                "VALUES ('case-1', 'import-1', 'opportunity', 'opportunity-1', 'opportunity-2', "
                "'Possible duplicate', 0.8, '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO duplicate_case_source_references (duplicate_case_id, source_reference_id) "
                "VALUES ('case-1', 'ref-1')"
            )
        )


def test_duplicate_decision_migration_preserves_case_and_enforces_history_constraints(tmp_path: Path) -> None:
    database = tmp_path / "duplicate-decisions.db"
    migrate(database, "0012")
    seed_duplicate_case(database)
    migrate(database, "head")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "duplicate_case_decisions" in inspector.get_table_names()
    assert ("uq_duplicate_case_decisions_sequence", ("duplicate_case_id", "sequence")) in [
        (constraint["name"], tuple(constraint["column_names"]))
        for constraint in inspector.get_unique_constraints("duplicate_case_decisions")
    ]

    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO duplicate_case_decisions "
                "(id, duplicate_case_id, sequence, outcome, reason, decided_at) "
                "VALUES ('decision-1', 'case-1', 1, 'confirmed_duplicate', 'Same role.', '2026-08-17')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO duplicate_case_decisions "
                "(id, duplicate_case_id, sequence, outcome, reason, decided_at) "
                "VALUES ('decision-2', 'case-1', 2, 'keep_unresolved', 'Review later.', '2026-08-17')"
            )
        )

    invalid_rows = [
        ("bad-sequence", 0, "confirmed_distinct", "Reason"),
        ("bad-outcome", 3, "merged", "Reason"),
        ("bad-reason", 3, "confirmed_distinct", "   "),
        ("duplicate-sequence", 2, "confirmed_distinct", "Reason"),
    ]
    for decision_id, sequence, outcome, reason in invalid_rows:
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO duplicate_case_decisions "
                        "(id, duplicate_case_id, sequence, outcome, reason, decided_at) "
                        "VALUES (:id, 'case-1', :sequence, :outcome, :reason, '2026-08-17')"
                    ),
                    {"id": decision_id, "sequence": sequence, "outcome": outcome, "reason": reason},
                )

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases WHERE id = 'case-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_case_decisions WHERE duplicate_case_id = 'case-1'")) == 2


def test_duplicate_decisions_cascade_and_downgrade_only_remove_decision_history(tmp_path: Path) -> None:
    cascade_db = tmp_path / "duplicate-decision-cascade.db"
    migrate(cascade_db, "0012")
    seed_duplicate_case(cascade_db)
    migrate(cascade_db, "head")
    engine = create_engine(f"sqlite:///{cascade_db.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO duplicate_case_decisions "
                "(id, duplicate_case_id, sequence, outcome, reason, decided_at) "
                "VALUES ('decision-1', 'case-1', 1, 'confirmed_distinct', 'Different roles.', '2026-08-17')"
            )
        )
        connection.execute(text("DELETE FROM duplicate_cases WHERE id = 'case-1'"))
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_case_decisions")) == 0
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities")) == 2

    downgrade_db = tmp_path / "duplicate-decision-downgrade.db"
    migrate(downgrade_db, "0012")
    seed_duplicate_case(downgrade_db)
    migrate(downgrade_db, "head")
    downgrade_engine = create_engine(f"sqlite:///{downgrade_db.as_posix()}")
    with downgrade_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO duplicate_case_decisions "
                "(id, duplicate_case_id, sequence, outcome, reason, decided_at) "
                "VALUES ('decision-1', 'case-1', 1, 'related_but_distinct', 'Related role.', '2026-08-17')"
            )
        )

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{downgrade_db.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0012")

    inspector = inspect(create_engine(f"sqlite:///{downgrade_db.as_posix()}"))
    assert "duplicate_case_decisions" not in inspector.get_table_names()
    with create_engine(f"sqlite:///{downgrade_db.as_posix()}").connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases WHERE id = 'case-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities")) == 2
