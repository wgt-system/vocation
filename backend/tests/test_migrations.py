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
            "uniques": sorted(
                (constraint["name"], tuple(constraint["column_names"])) for constraint in inspector.get_unique_constraints(table)
            ),
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


def seed_v020_data(database: Path) -> None:
    seed_v010_data(database)
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("UPDATE opportunities SET tracking_status = 'shortlisted' WHERE id = 'opportunity-1'"))
        connection.execute(
            text(
                "INSERT INTO personal_assessments "
                "(id, opportunity_id, criterion_id, value_json, created_at, revision_number, origin) "
                "VALUES ('assessment-1','opportunity-1','junior_suitability','5','2025-01-01',1,'personal')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO opportunity_decisions "
                "(id, opportunity_id, decision_type, previous_status, resulting_status, created_at) "
                "VALUES ('decision-1','opportunity-1','status_change','new','shortlisted','2025-01-01')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO source_references "
                "(id, import_id, bundle_local_id, source_id, url, normalized_url, observed_at) "
                "VALUES ('ref-2','import-1','ref-2','source-1','https://example.test/other',"
                "'https://example.test/other','2025-01-01 00:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO opportunities "
                "(id, import_id, bundle_local_id, company_id, canonical_title, source_reference_id, observed_at) "
                "VALUES ('opportunity-2','import-1','opportunity-2','company-1','Another Engineer','ref-2',"
                "'2025-01-01 00:00:00')"
            )
        )


def insert_duplicate_case(database: Path, case_id: str = "case-1") -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO duplicate_cases "
                "(id, research_import_id, subject_type, left_subject_id, right_subject_id, evidence_summary, confidence, created_at) "
                "VALUES (:id, 'import-1', 'opportunity', 'opportunity-1', 'opportunity-2', "
                "'Similar role and employer evidence', 0.75, '2025-01-01')"
            ),
            {"id": case_id},
        )
        connection.execute(
            text("INSERT INTO duplicate_case_source_references (duplicate_case_id, source_reference_id) VALUES (:id, 'ref-1')"),
            {"id": case_id},
        )


def insert_prompt_context_snapshot(
    database: Path,
    prompt_context_ref: str = "context-1",
    fingerprint: str = "a" * 64,
    correlation_ref: str = "correlation-1",
    subject_type: str = "opportunity",
    subject_id: str = "opportunity-1",
) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO prompt_context_snapshots "
                "(prompt_context_ref, scope_type, as_of_date, scope_json, fingerprint, created_at) "
                "VALUES (:prompt_context_ref, 'opportunity_update', '2026-08-08', "
                '\'{"type":"opportunity_update","as_of_date":"2026-08-08"}\', :fingerprint, \'2026-08-08\')'
            ),
            {"prompt_context_ref": prompt_context_ref, "fingerprint": fingerprint},
        )
        connection.execute(
            text(
                "INSERT INTO prompt_context_subjects "
                "(prompt_context_ref, correlation_ref, subject_type, subject_id, is_target) "
                "VALUES (:prompt_context_ref, :correlation_ref, :subject_type, :subject_id, 1)"
            ),
            {
                "prompt_context_ref": prompt_context_ref,
                "correlation_ref": correlation_ref,
                "subject_type": subject_type,
                "subject_id": subject_id,
            },
        )


def insert_prompt_run(
    database: Path,
    prompt_run_id: str,
    *,
    search_profile: str | None,
    prompt_context_ref: str | None,
    bundle_version: str = "1.0",
) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO prompt_runs "
                "(id, prompt_type, prompt_version, bundle_version, search_profile, prompt_context_ref, "
                "constraints_json, as_of_date, criteria_snapshot_json, prompt_text, generated_at) "
                "VALUES (:id, 'opportunity_update', '1.0', :bundle_version, :search_profile, :prompt_context_ref, "
                "'{}', '2026-08-08', '{}', 'prompt', '2026-08-08')"
            ),
            {
                "id": prompt_run_id,
                "bundle_version": bundle_version,
                "search_profile": search_profile,
                "prompt_context_ref": prompt_context_ref,
            },
        )


def insert_research_import_with_context(
    database: Path,
    import_id: str,
    prompt_context_ref: str,
    bundle_version: str = "2.0",
) -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO research_imports "
                "(id, status, bundle_version, prompt_context_ref, created_at, counts_json, warnings_json) "
                "VALUES (:id, 'applied', :bundle_version, :prompt_context_ref, '2026-08-08', '{}', '[]')"
            ),
            {
                "id": import_id,
                "bundle_version": bundle_version,
                "prompt_context_ref": prompt_context_ref,
            },
        )


def insert_initial_prompt_run(database: Path, prompt_run_id: str = "prompt-initial") -> None:
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO prompt_runs "
                "(id, prompt_type, prompt_version, bundle_version, search_profile, constraints_json, "
                "as_of_date, criteria_snapshot_json, prompt_text, generated_at) "
                "VALUES (:id, 'initial_market_research', '1.0', '1.0', 'Junior software roles', "
                "'{}', '2026-08-08', '{}', 'prompt', '2026-08-08')"
            ),
            {"id": prompt_run_id},
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
    assert "duplicate_cases" not in inspector.get_table_names()
    assert "duplicate_case_source_references" not in inspector.get_table_names()
    assert "tracking_status" not in {column["name"] for column in inspector.get_columns("opportunities")}


def test_v020_integrity_constraints_are_present_and_enforced(tmp_path: Path) -> None:
    database = tmp_path / "integrity.db"
    migrate(database, "head")
    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert ("uq_personal_assessment_revision", ("opportunity_id", "criterion_id", "revision_number")) in schema(database)[
        "personal_assessments"
    ]["uniques"]
    assert ("uq_personal_assessment_predecessor", ("supersedes_id",)) in schema(database)["personal_assessments"]["uniques"]
    assert ("uq_opportunity_decision_reversal", ("reverses_decision_id",)) in schema(database)["opportunity_decisions"]["uniques"]
    checks = {
        item["sqltext"] for table in ("personal_assessments", "opportunity_decisions") for item in inspector.get_check_constraints(table)
    }
    assert any("revision_number >= 1" in check for check in checks)
    assert any("origin = 'personal'" in check for check in checks)

    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO personal_assessments "
                "(id, opportunity_id, criterion_id, value_json, created_at, revision_number, origin) "
                "VALUES ('a1','o1','c1','4','2025-01-01',1,'personal')"
            )
        )
        try:
            connection.execute(
                text(
                    "INSERT INTO personal_assessments "
                    "(id, opportunity_id, criterion_id, value_json, created_at, revision_number, origin) "
                    "VALUES ('a2','o1','c1','5','2025-01-01',0,'personal')"
                )
            )
        except Exception:
            pass
        else:
            raise AssertionError("revision_number check must reject zero")


def test_duplicate_case_fresh_and_v020_upgrade_preserve_data_and_restart(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh-duplicate.db"
    v020 = tmp_path / "v020-duplicate.db"
    migrate(fresh, "head")
    fresh_inspector = inspect(create_engine(f"sqlite:///{fresh.as_posix()}"))
    assert {"duplicate_cases", "duplicate_case_source_references"}.issubset(fresh_inspector.get_table_names())
    assert (
        "uq_duplicate_case_subject_pair",
        ("subject_type", "left_subject_id", "right_subject_id"),
    ) in schema_for_duplicate_cases(fresh)["uniques"]

    migrate(v020, "0004")
    seed_v020_data(v020)
    migrate(v020, "head")
    insert_duplicate_case(v020)

    engine = create_engine(f"sqlite:///{v020.as_posix()}")
    engine.dispose()
    restarted = create_engine(f"sqlite:///{v020.as_posix()}")
    with restarted.connect() as connection:
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
        assert connection.scalar(text("SELECT value_json FROM personal_assessments WHERE id = 'assessment-1'")) == "5"
        assert connection.scalar(text("SELECT resulting_status FROM opportunity_decisions WHERE id = 'decision-1'")) == "shortlisted"
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_case_source_references")) == 1


def schema_for_duplicate_cases(database: Path) -> dict:
    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    return {
        "uniques": [
            (constraint["name"], tuple(constraint["column_names"])) for constraint in inspector.get_unique_constraints("duplicate_cases")
        ],
        "checks": [check["name"] for check in inspector.get_check_constraints("duplicate_cases")],
    }


def test_duplicate_case_constraints_and_cascade_are_enforced(tmp_path: Path) -> None:
    database = tmp_path / "duplicate-constraints.db"
    migrate(database, "0004")
    seed_v020_data(database)
    migrate(database, "head")
    insert_duplicate_case(database)
    engine = create_engine(f"sqlite:///{database.as_posix()}")

    invalid_cases = [
        ("case-self", "opportunity", "opportunity-1", "opportunity-1", "valid", 0.5),
        ("case-type", "company", "a", "b", "valid", 0.5),
        ("case-confidence-low", "opportunity", "a", "b", "valid", -0.01),
        ("case-confidence-high", "opportunity", "c", "d", "valid", 1.01),
        ("case-empty-evidence", "opportunity", "e", "f", "   ", 0.5),
    ]
    for case_id, subject_type, left_id, right_id, evidence, confidence in invalid_cases:
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO duplicate_cases "
                        "(id, research_import_id, subject_type, left_subject_id, right_subject_id, "
                        "evidence_summary, confidence, created_at) "
                        "VALUES (:id, 'import-1', :subject_type, :left_id, :right_id, :evidence, :confidence, '2025-01-01')"
                    ),
                    {
                        "id": case_id,
                        "subject_type": subject_type,
                        "left_id": left_id,
                        "right_id": right_id,
                        "evidence": evidence,
                        "confidence": confidence,
                    },
                )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO duplicate_cases "
                    "(id, research_import_id, subject_type, left_subject_id, right_subject_id, evidence_summary, confidence, created_at) "
                    "VALUES ('case-duplicate', 'import-1', 'opportunity', 'opportunity-1', 'opportunity-2', 'Same pair', 0.5, '2025-01-01')"
                )
            )

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO duplicate_case_source_references (duplicate_case_id, source_reference_id) VALUES ('case-1', 'ref-1')")
            )

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(text("DELETE FROM duplicate_cases WHERE id = 'case-1'"))
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_case_source_references")) == 0
        assert connection.scalar(text("SELECT COUNT(*) FROM source_references WHERE id = 'ref-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities WHERE id IN ('opportunity-1', 'opportunity-2')")) == 2


def test_duplicate_case_migration_downgrades_without_touching_v020_data(tmp_path: Path) -> None:
    database = tmp_path / "duplicate-downgrade.db"
    migrate(database, "0004")
    seed_v020_data(database)
    migrate(database, "head")
    insert_duplicate_case(database)

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0004")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "duplicate_cases" not in inspector.get_table_names()
    assert "duplicate_case_source_references" not in inspector.get_table_names()
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1


def test_prompt_context_fresh_and_v03_upgrade_preserve_data_and_restart(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh-context.db"
    v03 = tmp_path / "v03-context.db"
    migrate(fresh, "head")
    fresh_inspector = inspect(create_engine(f"sqlite:///{fresh.as_posix()}"))
    assert {"prompt_context_snapshots", "prompt_context_subjects"}.issubset(fresh_inspector.get_table_names())

    migrate(v03, "0005")
    seed_v020_data(v03)
    insert_duplicate_case(v03)
    migrate(v03, "head")
    insert_prompt_context_snapshot(v03)

    engine = create_engine(f"sqlite:///{v03.as_posix()}")
    engine.dispose()
    restarted = create_engine(f"sqlite:///{v03.as_posix()}")
    with restarted.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases")) == 1
        assert connection.scalar(text("SELECT tracking_status FROM opportunities WHERE id = 'opportunity-1'")) == "shortlisted"
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_snapshots")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_subjects")) == 1
        assert connection.scalar(text("SELECT scope_json FROM prompt_context_snapshots WHERE prompt_context_ref = 'context-1'")) == (
            '{"type":"opportunity_update","as_of_date":"2026-08-08"}'
        )


def test_prompt_context_constraints_and_snapshot_cascade_are_enforced(tmp_path: Path) -> None:
    database = tmp_path / "context-constraints.db"
    migrate(database, "0005")
    seed_v020_data(database)
    insert_duplicate_case(database)
    migrate(database, "head")
    insert_prompt_context_snapshot(database)
    engine = create_engine(f"sqlite:///{database.as_posix()}")

    invalid_snapshots = [
        ("context-invalid-scope", "not_a_scope", "b" * 64),
        ("context-1", "opportunity_update", "c" * 64),
        ("context-duplicate-fingerprint", "opportunity_update", "a" * 64),
    ]
    for prompt_context_ref, scope_type, fingerprint in invalid_snapshots:
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO prompt_context_snapshots "
                        "(prompt_context_ref, scope_type, as_of_date, scope_json, fingerprint, created_at) "
                        "VALUES (:prompt_context_ref, :scope_type, '2026-08-08', '{}', :fingerprint, '2026-08-08')"
                    ),
                    {"prompt_context_ref": prompt_context_ref, "scope_type": scope_type, "fingerprint": fingerprint},
                )

    insert_prompt_context_snapshot(database, prompt_context_ref="context-2", fingerprint="d" * 64)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.commit()
    with engine.begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO prompt_context_subjects "
                    "(prompt_context_ref, correlation_ref, subject_type, subject_id, is_target) "
                    "VALUES ('context-1', 'correlation-1', 'opportunity', 'opportunity-1', 1)"
                )
            )
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO prompt_context_subjects "
                    "(prompt_context_ref, correlation_ref, subject_type, subject_id, is_target) "
                    "VALUES ('context-1', 'correlation-2', 'opportunity', 'opportunity-1', 1)"
                )
            )
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO prompt_context_subjects "
                    "(prompt_context_ref, correlation_ref, subject_type, subject_id, is_target) "
                    "VALUES ('context-1', 'correlation-invalid', 'company_group', 'company-1', 0)"
                )
            )

        connection.execute(text("DELETE FROM prompt_context_snapshots WHERE prompt_context_ref = 'context-1'"))
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_subjects WHERE prompt_context_ref = 'context-1'")) == 0
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_snapshots WHERE prompt_context_ref = 'context-2'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_subjects WHERE prompt_context_ref = 'context-2'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM source_references")) == 2
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunities")) == 2


def test_prompt_context_downgrade_to_0005_preserves_vocation_data(tmp_path: Path) -> None:
    database = tmp_path / "context-downgrade.db"
    migrate(database, "0005")
    seed_v020_data(database)
    insert_duplicate_case(database)
    migrate(database, "head")
    insert_prompt_context_snapshot(database)

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0005")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "prompt_context_snapshots" not in inspector.get_table_names()
    assert "prompt_context_subjects" not in inspector.get_table_names()
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM duplicate_cases")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1


def test_prompt_context_links_fresh_and_0006_upgrade_backfill_and_restart(tmp_path: Path) -> None:
    fresh = tmp_path / "fresh-0007.db"
    migrated = tmp_path / "migrated-0007.db"
    migrate(fresh, "head")
    fresh_inspector = inspect(create_engine(f"sqlite:///{fresh.as_posix()}"))
    assert "prompt_context_ref" in {column["name"] for column in fresh_inspector.get_columns("prompt_runs")}
    assert "bundle_version" in {column["name"] for column in fresh_inspector.get_columns("research_imports")}
    assert any(column["name"] == "search_profile" and column["nullable"] for column in fresh_inspector.get_columns("prompt_runs"))
    assert ("uq_prompt_runs_prompt_context_ref", ("prompt_context_ref",)) in [
        (constraint["name"], tuple(constraint["column_names"])) for constraint in fresh_inspector.get_unique_constraints("prompt_runs")
    ]
    for table in ("prompt_runs", "research_imports"):
        foreign_key = next(
            foreign_key
            for foreign_key in fresh_inspector.get_foreign_keys(table)
            if foreign_key["referred_table"] == "prompt_context_snapshots"
        )
        assert foreign_key.get("options", {}).get("ondelete") is None

    migrate(migrated, "0006")
    seed_v020_data(migrated)
    insert_initial_prompt_run(migrated)
    insert_duplicate_case(migrated)
    insert_prompt_context_snapshot(migrated)
    migrate(migrated, "head")
    insert_prompt_run(migrated, "prompt-update-1", search_profile=None, prompt_context_ref="context-1", bundle_version="2.0")
    insert_research_import_with_context(migrated, "import-update-1", "context-1")
    insert_research_import_with_context(migrated, "import-update-2", "context-1")

    with pytest.raises(IntegrityError):
        insert_prompt_run(migrated, "prompt-update-2", search_profile=None, prompt_context_ref="context-1", bundle_version="2.0")

    engine = create_engine(f"sqlite:///{migrated.as_posix()}")
    engine.dispose()
    restarted = create_engine(f"sqlite:///{migrated.as_posix()}")
    with restarted.connect() as connection:
        assert connection.scalar(text("SELECT bundle_version FROM research_imports WHERE id = 'import-1'")) == "1.0"
        assert connection.scalar(text("SELECT search_profile FROM prompt_runs WHERE id = 'prompt-initial'")) == "Junior software roles"
        assert connection.scalar(text("SELECT search_profile FROM prompt_runs WHERE id = 'prompt-update-1'")) is None
        assert connection.scalar(text("SELECT COUNT(*) FROM research_imports WHERE prompt_context_ref = 'context-1'")) == 2
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1
        assert (
            connection.scalar(
                text(
                    "SELECT subject_type || ':' || left_subject_id || ':' || right_subject_id || ':' || evidence_summary "
                    "FROM duplicate_cases WHERE id = 'case-1'"
                )
            )
            == "opportunity:opportunity-1:opportunity-2:Similar role and employer evidence"
        )
        assert (
            connection.scalar(text("SELECT source_reference_id FROM duplicate_case_source_references WHERE duplicate_case_id = 'case-1'"))
            == "ref-1"
        )


def test_prompt_context_links_downgrade_to_0006_preserves_preexisting_data(tmp_path: Path) -> None:
    database = tmp_path / "downgrade-0007.db"
    migrate(database, "0006")
    seed_v020_data(database)
    insert_initial_prompt_run(database)
    insert_prompt_context_snapshot(database)
    migrate(database, "head")
    insert_prompt_run(database, "prompt-update-1", search_profile=None, prompt_context_ref="context-1", bundle_version="2.0")
    insert_research_import_with_context(database, "import-update-1", "context-1")

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0006")

    inspector = inspect(create_engine(f"sqlite:///{database.as_posix()}"))
    assert "prompt_context_ref" not in {column["name"] for column in inspector.get_columns("prompt_runs")}
    assert "bundle_version" not in {column["name"] for column in inspector.get_columns("research_imports")}
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_runs WHERE id = 'prompt-initial'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM research_imports WHERE id = 'import-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_snapshots WHERE prompt_context_ref = 'context-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM prompt_context_subjects WHERE prompt_context_ref = 'context-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1


def test_availability_0008_upgrade_and_downgrade_preserves_research_and_personal_state(tmp_path: Path) -> None:
    fresh = tmp_path / "availability-fresh.db"
    migrate(fresh, "head")
    fresh_inspector = inspect(create_engine(f"sqlite:///{fresh.as_posix()}"))
    assert "availability_observations" in fresh_inspector.get_table_names()
    assert {column["name"] for column in fresh_inspector.get_columns("availability_observations")} == {
        "id",
        "import_id",
        "bundle_local_id",
        "posting_id",
        "result",
        "observed_at",
        "evidence_summary",
        "recorded_at",
    }
    import_columns = {column["name"]: column for column in fresh_inspector.get_columns("research_imports")}
    assert import_columns["import_kind"]["nullable"] is False
    assert any("availability_check" in check["sqltext"] for check in fresh_inspector.get_check_constraints("research_imports"))

    migrated = tmp_path / "availability-from-0007.db"
    migrate(migrated, "0007")
    seed_v020_data(migrated)
    migrate(migrated, "head")
    engine = create_engine(f"sqlite:///{migrated.as_posix()}")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT import_kind FROM research_imports WHERE id = 'import-1'")) == "research"
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{migrated.as_posix()}")
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    command.downgrade(config, "0007")
    downgraded = inspect(create_engine(f"sqlite:///{migrated.as_posix()}"))
    assert "availability_observations" not in downgraded.get_table_names()
    assert "import_kind" not in {column["name"] for column in downgraded.get_columns("research_imports")}
    with create_engine(f"sqlite:///{migrated.as_posix()}").connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM personal_assessments WHERE id = 'assessment-1'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM opportunity_decisions WHERE id = 'decision-1'")) == 1
