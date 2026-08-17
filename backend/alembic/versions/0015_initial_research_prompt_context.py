"""Allow Initial Research to use persisted prompt context snapshots."""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("prompt_context_snapshots", recreate="always") as batch:
        batch.drop_constraint("ck_prompt_context_snapshot_scope_type", type_="check")
        batch.create_check_constraint(
            "ck_prompt_context_snapshot_scope_type",
            "scope_type IN ('initial_market_research','full_update','company_update','opportunity_update','gap_filling','availability_check')",
        )


def downgrade() -> None:
    with op.batch_alter_table("prompt_context_snapshots", recreate="always") as batch:
        batch.drop_constraint("ck_prompt_context_snapshot_scope_type", type_="check")
        batch.create_check_constraint(
            "ck_prompt_context_snapshot_scope_type",
            "scope_type IN ('full_update','company_update','opportunity_update','gap_filling','availability_check')",
        )
