"""Persist prompt context snapshots and their scoped subject mappings."""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_context_snapshots",
        sa.Column("prompt_context_ref", sa.String(200), primary_key=True),
        sa.Column("scope_type", sa.String(30), nullable=False),
        sa.Column("as_of_date", sa.String(10), nullable=False),
        sa.Column("scope_json", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("fingerprint", name="uq_prompt_context_snapshots_fingerprint"),
        sa.CheckConstraint(
            "scope_type IN ('full_update','company_update','opportunity_update','gap_filling')",
            name="ck_prompt_context_snapshot_scope_type",
        ),
        sa.CheckConstraint("length(prompt_context_ref) > 0 AND length(prompt_context_ref) <= 200", name="ck_prompt_context_ref_length"),
        sa.CheckConstraint("length(fingerprint) = 64", name="ck_prompt_context_fingerprint_length"),
    )
    op.create_table(
        "prompt_context_subjects",
        sa.Column(
            "prompt_context_ref",
            sa.String(200),
            sa.ForeignKey("prompt_context_snapshots.prompt_context_ref", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("correlation_ref", sa.String(200), primary_key=True),
        sa.Column("subject_type", sa.String(20), nullable=False),
        sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("is_target", sa.Boolean(), nullable=False),
        sa.UniqueConstraint(
            "prompt_context_ref",
            "subject_type",
            "subject_id",
            name="uq_prompt_context_subject_subject",
        ),
        sa.CheckConstraint("subject_type IN ('company','opportunity','posting')", name="ck_prompt_context_subject_type"),
        sa.CheckConstraint(
            "length(correlation_ref) > 0 AND length(correlation_ref) <= 200",
            name="ck_prompt_context_correlation_ref_length",
        ),
    )
    op.create_index("ix_prompt_context_subjects_subject_id", "prompt_context_subjects", ["subject_id"])


def downgrade() -> None:
    op.drop_table("prompt_context_subjects")
    op.drop_table("prompt_context_snapshots")
