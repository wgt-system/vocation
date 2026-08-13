"""Persist application cases and immutable material revisions."""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

_LIFECYCLES = "'draft','ready','submitted','interviewing','offer','accepted','rejected','withdrawn'"
_MATERIAL_KINDS = "'cv','cover_letter','other'"


def upgrade() -> None:
    op.create_table(
        "application_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id"), nullable=False),
        sa.Column("lifecycle", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(f"lifecycle IN ({_LIFECYCLES})", name="ck_application_cases_lifecycle"),
    )
    op.create_index("ix_application_cases_opportunity_id", "application_cases", ["opportunity_id"])
    op.create_index(
        "uq_application_cases_one_active_per_opportunity",
        "application_cases",
        ["opportunity_id"],
        unique=True,
        sqlite_where=sa.text("lifecycle NOT IN ('accepted','rejected','withdrawn')"),
    )

    op.create_table(
        "application_case_lifecycle_events",
        sa.Column(
            "application_case_id",
            sa.String(36),
            sa.ForeignKey("application_cases.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("sequence", sa.Integer(), primary_key=True),
        sa.Column("previous_status", sa.String(30)),
        sa.Column("resulting_status", sa.String(30), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("sequence >= 1", name="ck_application_case_lifecycle_events_sequence"),
        sa.CheckConstraint(
            f"previous_status IS NULL OR previous_status IN ({_LIFECYCLES})",
            name="ck_application_case_lifecycle_events_previous_status",
        ),
        sa.CheckConstraint(
            f"resulting_status IN ({_LIFECYCLES})",
            name="ck_application_case_lifecycle_events_resulting_status",
        ),
    )

    op.create_table(
        "application_materials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "application_case_id",
            sa.String(36),
            sa.ForeignKey("application_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(f"kind IN ({_MATERIAL_KINDS})", name="ck_application_materials_kind"),
    )
    op.create_index("ix_application_materials_application_case_id", "application_materials", ["application_case_id"])

    op.create_table(
        "application_material_revisions",
        sa.Column(
            "material_id",
            sa.String(36),
            sa.ForeignKey("application_materials.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("revision", sa.Integer(), primary_key=True),
        sa.Column("display_name", sa.String(300), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("revision >= 1", name="ck_application_material_revisions_revision"),
        sa.CheckConstraint(
            "length(trim(display_name)) > 0",
            name="ck_application_material_revisions_display_name_nonempty",
        ),
    )


def downgrade() -> None:
    op.drop_table("application_material_revisions")
    op.drop_index("ix_application_materials_application_case_id", table_name="application_materials")
    op.drop_table("application_materials")
    op.drop_table("application_case_lifecycle_events")
    op.drop_index("uq_application_cases_one_active_per_opportunity", table_name="application_cases")
    op.drop_index("ix_application_cases_opportunity_id", table_name="application_cases")
    op.drop_table("application_cases")
