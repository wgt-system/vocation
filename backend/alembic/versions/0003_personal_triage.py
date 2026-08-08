"""Add the v0.2 personal triage schema."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

TRACKING_STATUSES = "'new','to_review','interesting','shortlisted','deferred','excluded','archived'"


def upgrade() -> None:
    with op.batch_alter_table("opportunities") as batch:
        batch.add_column(sa.Column("tracking_status", sa.String(30), nullable=False, server_default="new"))
        batch.create_check_constraint("ck_opportunities_tracking_status", f"tracking_status IN ({TRACKING_STATUSES})")
    op.create_index("ix_opportunities_tracking_status", "opportunities", ["tracking_status"])
    op.create_table(
        "personal_assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("criterion_id", sa.String(100), sa.ForeignKey("assessment_criteria.criterion_id"), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=False), sa.Column("reasoning", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("supersedes_id", sa.String(36), sa.ForeignKey("personal_assessments.id")),
        sa.Column("revision_number", sa.Integer(), nullable=False), sa.Column("origin", sa.String(30), nullable=False, server_default="personal"),
    )
    op.create_index("ix_personal_assessments_opportunity_id", "personal_assessments", ["opportunity_id"])
    op.create_index("ix_personal_assessments_criterion_id", "personal_assessments", ["criterion_id"])
    op.create_index("ix_personal_assessments_supersedes_id", "personal_assessments", ["supersedes_id"])
    op.create_table(
        "opportunity_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision_type", sa.String(30), nullable=False),
        sa.Column("previous_status", sa.String(30), nullable=False), sa.Column("resulting_status", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reverses_decision_id", sa.String(36), sa.ForeignKey("opportunity_decisions.id")),
        sa.CheckConstraint("decision_type IN ('status_change','exclusion','restore')", name="ck_decision_type"),
        sa.CheckConstraint(f"previous_status IN ({TRACKING_STATUSES})", name="ck_decision_previous_status"),
        sa.CheckConstraint(f"resulting_status IN ({TRACKING_STATUSES})", name="ck_decision_resulting_status"),
    )
    op.create_index("ix_opportunity_decisions_opportunity_id", "opportunity_decisions", ["opportunity_id"])
    op.create_index("ix_opportunity_decisions_reverses_decision_id", "opportunity_decisions", ["reverses_decision_id"])


def downgrade() -> None:
    op.drop_table("opportunity_decisions")
    op.drop_table("personal_assessments")
    op.drop_index("ix_opportunities_tracking_status", table_name="opportunities")
    with op.batch_alter_table("opportunities") as batch:
        batch.drop_constraint("ck_opportunities_tracking_status", type_="check")
        batch.drop_column("tracking_status")
