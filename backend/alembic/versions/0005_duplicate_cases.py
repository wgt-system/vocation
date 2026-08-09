"""Persist unresolved possible duplicate cases and their evidence references."""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "duplicate_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("research_import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("subject_type", sa.String(20), nullable=False),
        sa.Column("left_subject_id", sa.String(36), nullable=False),
        sa.Column("right_subject_id", sa.String(36), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "subject_type",
            "left_subject_id",
            "right_subject_id",
            name="uq_duplicate_case_subject_pair",
        ),
        sa.CheckConstraint("subject_type IN ('opportunity','posting')", name="ck_duplicate_case_subject_type"),
        sa.CheckConstraint("left_subject_id <> right_subject_id", name="ck_duplicate_case_distinct_subjects"),
        sa.CheckConstraint("length(trim(evidence_summary)) > 0", name="ck_duplicate_case_evidence_nonempty"),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_duplicate_case_confidence_range",
        ),
    )
    op.create_index("ix_duplicate_cases_research_import_id", "duplicate_cases", ["research_import_id"])
    op.create_table(
        "duplicate_case_source_references",
        sa.Column(
            "duplicate_case_id",
            sa.String(36),
            sa.ForeignKey("duplicate_cases.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), primary_key=True),
    )
    op.create_index(
        "ix_duplicate_case_source_references_source_reference_id",
        "duplicate_case_source_references",
        ["source_reference_id"],
    )


def downgrade() -> None:
    op.drop_table("duplicate_case_source_references")
    op.drop_table("duplicate_cases")
