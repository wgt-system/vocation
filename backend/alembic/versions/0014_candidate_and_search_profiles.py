"""Persist private candidate profile revisions and Vocation search profiles."""

from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidate_profile_revisions",
        sa.Column("revision", sa.Integer(), primary_key=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("revision >= 1", name="ck_candidate_profile_revisions_revision"),
        sa.CheckConstraint("length(payload_json) > 2", name="ck_candidate_profile_revisions_payload"),
    )

    op.create_table(
        "search_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("current_revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_search_profiles_name"),
        sa.CheckConstraint("current_revision >= 1", name="ck_search_profiles_current_revision"),
    )
    op.create_index(
        "uq_search_profiles_single_default",
        "search_profiles",
        ["is_default"],
        unique=True,
        sqlite_where=sa.text("is_default = 1"),
    )

    op.create_table(
        "search_profile_revisions",
        sa.Column(
            "search_profile_id",
            sa.String(36),
            sa.ForeignKey("search_profiles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("revision", sa.Integer(), primary_key=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("revision >= 1", name="ck_search_profile_revisions_revision"),
        sa.CheckConstraint("length(payload_json) > 2", name="ck_search_profile_revisions_payload"),
    )
    op.create_index(
        "ix_search_profile_revisions_profile",
        "search_profile_revisions",
        ["search_profile_id", "revision"],
    )


def downgrade() -> None:
    op.drop_table("search_profile_revisions")
    op.drop_index("uq_search_profiles_single_default", table_name="search_profiles")
    op.drop_table("search_profiles")
    op.drop_table("candidate_profile_revisions")
