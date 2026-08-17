"""Persist Opportunity Groups and ordered memberships."""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "opportunity_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("group_type", sa.String(30), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_opportunity_groups_name_nonempty"),
        sa.CheckConstraint("group_type IN ('general','application_wave')", name="ck_opportunity_groups_group_type"),
    )
    op.create_table(
        "opportunity_group_memberships",
        sa.Column("group_id", sa.String(36), sa.ForeignKey("opportunity_groups.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id"), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("group_id", "position", name="uq_opportunity_group_memberships_position"),
        sa.CheckConstraint("position >= 0", name="ck_opportunity_group_memberships_position_nonnegative"),
    )
    op.create_index("ix_opportunity_group_memberships_opportunity_id", "opportunity_group_memberships", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_opportunity_group_memberships_opportunity_id", table_name="opportunity_group_memberships")
    op.drop_table("opportunity_group_memberships")
    op.drop_table("opportunity_groups")
