"""Persist append-only duplicate case review decisions."""

from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


OUTCOMES = (
    "confirmed_duplicate",
    "confirmed_distinct",
    "related_but_distinct",
    "keep_unresolved",
)


def upgrade() -> None:
    op.create_table(
        "duplicate_case_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "duplicate_case_id",
            sa.String(36),
            sa.ForeignKey("duplicate_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "duplicate_case_id",
            "sequence",
            name="uq_duplicate_case_decisions_sequence",
        ),
        sa.CheckConstraint("sequence >= 1", name="ck_duplicate_case_decisions_sequence"),
        sa.CheckConstraint(
            "outcome IN ('confirmed_duplicate','confirmed_distinct','related_but_distinct','keep_unresolved')",
            name="ck_duplicate_case_decisions_outcome",
        ),
        sa.CheckConstraint(
            "length(trim(reason)) > 0",
            name="ck_duplicate_case_decisions_reason_nonempty",
        ),
    )
    op.create_index(
        "ix_duplicate_case_decisions_duplicate_case_id",
        "duplicate_case_decisions",
        ["duplicate_case_id"],
    )


def downgrade() -> None:
    op.drop_table("duplicate_case_decisions")
