"""Seed the initial Vocation assessment criteria.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    criteria = sa.table(
        "assessment_criteria",
        sa.column("criterion_id", sa.String),
        sa.column("display_name", sa.String),
        sa.column("description", sa.Text),
        sa.column("value_type", sa.String),
        sa.column("numeric_min", sa.Float),
        sa.column("numeric_max", sa.Float),
        sa.column("allowed_values_json", sa.Text),
        sa.column("applicable_subject_type", sa.String),
        sa.column("active", sa.Boolean),
        sa.column("display_order", sa.Integer),
        sa.column("revision", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        criteria,
        [
            {
                "criterion_id": "junior_suitability",
                "display_name": "Junior-Eignung",
                "description": "Wie gut passt die Stelle zu einem Berufseinstieg oder Junior-Profil?",
                "value_type": "numeric",
                "numeric_min": 1.0,
                "numeric_max": 5.0,
                "allowed_values_json": "[]",
                "applicable_subject_type": "opportunity",
                "active": True,
                "display_order": 10,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "criterion_id": "technology_fit",
                "display_name": "Technologie-Passung",
                "description": "Passung der geforderten Technologien zum Suchprofil.",
                "value_type": "numeric",
                "numeric_min": 1.0,
                "numeric_max": 5.0,
                "allowed_values_json": "[]",
                "applicable_subject_type": "opportunity",
                "active": True,
                "display_order": 20,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "criterion_id": "role_clarity",
                "display_name": "Rollenklarheit",
                "description": "Wie klar sind Aufgaben, Erwartungen und Verantwortlichkeiten beschrieben?",
                "value_type": "numeric",
                "numeric_min": 1.0,
                "numeric_max": 5.0,
                "allowed_values_json": "[]",
                "applicable_subject_type": "opportunity",
                "active": True,
                "display_order": 30,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "criterion_id": "work_model_fit",
                "display_name": "Arbeitsmodell-Passung",
                "description": "Externe Einschätzung des Arbeitsmodells gegenüber den Suchvorgaben.",
                "value_type": "categorical",
                "numeric_min": None,
                "numeric_max": None,
                "allowed_values_json": '["good", "acceptable", "poor", "unknown"]',
                "applicable_subject_type": "opportunity",
                "active": True,
                "display_order": 40,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM assessment_criteria WHERE criterion_id IN "
        "('junior_suitability', 'technology_fit', 'role_clarity', 'work_model_fit')"
    )
