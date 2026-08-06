"""Add immutable personal assessments and opportunity decisions."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "tracking_status" not in {column["name"] for column in inspector.get_columns("opportunities")}:
        with op.batch_alter_table("opportunities") as batch:
            batch.add_column(sa.Column("tracking_status", sa.String(length=30), nullable=False, server_default="new"))
    if "personal_assessments" not in inspector.get_table_names():
        op.create_table(
        "personal_assessments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("opportunity_id", sa.String(length=36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("criterion_id", sa.String(length=100), sa.ForeignKey("assessment_criteria.criterion_id"), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("supersedes_id", sa.String(length=36), sa.ForeignKey("personal_assessments.id")),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(length=30), nullable=False, server_default="personal"),
        )
    if "opportunity_decisions" not in inspector.get_table_names():
        op.create_table(
        "opportunity_decisions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("opportunity_id", sa.String(length=36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision_type", sa.String(length=30), nullable=False),
        sa.Column("previous_status", sa.String(length=30), nullable=False),
        sa.Column("resulting_status", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reverses_decision_id", sa.String(length=36), sa.ForeignKey("opportunity_decisions.id")),
        sa.CheckConstraint("decision_type IN ('status_change','exclusion','restore')", name="ck_decision_type"),
        )


def downgrade() -> None:
    op.drop_table("opportunity_decisions")
    op.drop_table("personal_assessments")
    with op.batch_alter_table("opportunities") as batch:
        batch.drop_constraint("ck_opportunities_tracking_status", type_="check")
        batch.drop_column("tracking_status")
