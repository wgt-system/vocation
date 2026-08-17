"""Persist availability-check import classification and observations."""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("research_imports", recreate="always") as batch:
        batch.add_column(sa.Column("import_kind", sa.String(30), nullable=False, server_default="research"))
        batch.create_check_constraint("ck_research_imports_import_kind", "import_kind IN ('research','availability_check')")

    with op.batch_alter_table("prompt_context_snapshots", recreate="always") as batch:
        batch.drop_constraint("ck_prompt_context_snapshot_scope_type", type_="check")
        batch.create_check_constraint(
            "ck_prompt_context_snapshot_scope_type",
            "scope_type IN ('full_update','company_update','opportunity_update','gap_filling','availability_check')",
        )

    op.create_table(
        "availability_observations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False),
        sa.Column("posting_id", sa.String(36), sa.ForeignKey("postings.id"), nullable=False),
        sa.Column("result", sa.String(40), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("import_id", "bundle_local_id", name="uq_availability_observations_import_bundle_id"),
        sa.UniqueConstraint("import_id", "posting_id", name="uq_availability_observations_import_posting"),
        sa.CheckConstraint(
            "result IN ('explicitly_available','explicitly_unavailable','temporarily_unreachable','not_found','indeterminate')",
            name="ck_availability_observations_result",
        ),
        sa.CheckConstraint("length(trim(evidence_summary)) > 0", name="ck_availability_observations_evidence_nonempty"),
    )
    op.create_index("ix_availability_observations_import_id", "availability_observations", ["import_id"])
    op.create_index("ix_availability_observations_posting_id", "availability_observations", ["posting_id"])
    op.create_index("ix_availability_observations_observed_at", "availability_observations", ["observed_at"])


def downgrade() -> None:
    op.drop_index("ix_availability_observations_observed_at", table_name="availability_observations")
    op.drop_index("ix_availability_observations_posting_id", table_name="availability_observations")
    op.drop_index("ix_availability_observations_import_id", table_name="availability_observations")
    op.drop_table("availability_observations")

    with op.batch_alter_table("prompt_context_snapshots", recreate="always") as batch:
        batch.drop_constraint("ck_prompt_context_snapshot_scope_type", type_="check")
        batch.create_check_constraint(
            "ck_prompt_context_snapshot_scope_type",
            "scope_type IN ('full_update','company_update','opportunity_update','gap_filling')",
        )
    with op.batch_alter_table("research_imports", recreate="always") as batch:
        batch.drop_constraint("ck_research_imports_import_kind", type_="check")
        batch.drop_column("import_kind")
