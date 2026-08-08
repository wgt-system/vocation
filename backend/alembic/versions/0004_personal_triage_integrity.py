"""Protect personal triage revision and reversal invariants."""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("personal_assessments") as batch:
        batch.create_unique_constraint("uq_personal_assessment_revision", ["opportunity_id", "criterion_id", "revision_number"])
        batch.create_unique_constraint("uq_personal_assessment_predecessor", ["supersedes_id"])
        batch.create_check_constraint("ck_personal_assessment_revision_positive", "revision_number >= 1")
        batch.create_check_constraint("ck_personal_assessment_origin", "origin = 'personal'")
    with op.batch_alter_table("opportunity_decisions") as batch:
        batch.create_unique_constraint("uq_opportunity_decision_reversal", ["reverses_decision_id"])


def downgrade() -> None:
    with op.batch_alter_table("opportunity_decisions") as batch:
        batch.drop_constraint("uq_opportunity_decision_reversal", type_="unique")
    with op.batch_alter_table("personal_assessments") as batch:
        batch.drop_constraint("ck_personal_assessment_origin", type_="check")
        batch.drop_constraint("ck_personal_assessment_revision_positive", type_="check")
        batch.drop_constraint("uq_personal_assessment_predecessor", type_="unique")
        batch.drop_constraint("uq_personal_assessment_revision", type_="unique")
