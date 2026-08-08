"""Initial Vocation milestone schema (the released v0.1.0 schema)."""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_imports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bundle_id", sa.String(200)),
        sa.Column("fingerprint", sa.String(64)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("counts_json", sa.Text(), nullable=False),
        sa.Column("warnings_json", sa.Text(), nullable=False),
    )
    op.create_index("ix_research_imports_fingerprint", "research_imports", ["fingerprint"])
    op.create_index("ix_research_imports_status", "research_imports", ["status"])
    op.create_table(
        "assessment_criteria",
        sa.Column("criterion_id", sa.String(100), primary_key=True),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(30), nullable=False),
        sa.Column("numeric_min", sa.Float()),
        sa.Column("numeric_max", sa.Float()),
        sa.Column("allowed_values_json", sa.Text(), nullable=False),
        sa.Column("applicable_subject_type", sa.String(30), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "prompt_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("prompt_type", sa.String(50), nullable=False),
        sa.Column("prompt_version", sa.String(20), nullable=False),
        sa.Column("bundle_version", sa.String(20), nullable=False),
        sa.Column("search_profile", sa.Text(), nullable=False),
        sa.Column("constraints_json", sa.Text(), nullable=False),
        sa.Column("as_of_date", sa.String(10), nullable=False),
        sa.Column("criteria_snapshot_json", sa.Text(), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "import_issues",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
    )
    op.create_index("ix_import_issues_import_id", "import_issues", ["import_id"])
    op.create_table(
        "sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("base_url", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    op.create_index("ix_sources_import_id", "sources", ["import_id"])
    op.create_table(
        "source_references",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("normalized_url", sa.Text(), nullable=False),
        sa.Column("external_reference_id", sa.String(300)),
        sa.Column("display_label", sa.String(300)),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    op.create_index("ix_source_references_import_id", "source_references", ["import_id"])
    op.create_index("ix_source_references_source_id", "source_references", ["source_id"])
    op.create_index("ix_source_references_normalized_url", "source_references", ["normalized_url"])
    op.create_table(
        "companies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False),
        sa.Column("canonical_name", sa.String(300), nullable=False),
        sa.Column("alternative_names_json", sa.Text(), nullable=False),
        sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_summary", sa.Text()),
        sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    op.create_index("ix_companies_import_id", "companies", ["import_id"])
    op.create_index("ix_companies_canonical_name", "companies", ["canonical_name"])
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("canonical_title", sa.String(300), nullable=False),
        sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_summary", sa.Text()),
        sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    op.create_index("ix_opportunities_import_id", "opportunities", ["import_id"])
    op.create_index("ix_opportunities_company_id", "opportunities", ["company_id"])
    op.create_index("ix_opportunities_canonical_title", "opportunities", ["canonical_title"])
    op.create_table(
        "work_locations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(300), nullable=False),
        sa.Column("city", sa.String(200)), sa.Column("region", sa.String(200)),
        sa.Column("country_code", sa.String(2)), sa.Column("precision", sa.String(30), nullable=False),
        sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("evidence_summary", sa.Text()),
    )
    op.create_index("ix_work_locations_opportunity_id", "work_locations", ["opportunity_id"])
    op.create_table(
        "postings",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False), sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("opportunity_id", sa.String(36), sa.ForeignKey("opportunities.id"), nullable=False), sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False), sa.Column("external_posting_id", sa.String(300)), sa.Column("stable_key", sa.Text(), nullable=False), sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("published_at", sa.String(10)), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("content_fingerprint", sa.String(200)),
        sa.UniqueConstraint("stable_key"), sa.UniqueConstraint("canonical_url"), sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    for column in ("import_id", "company_id", "opportunity_id"):
        op.create_index(f"ix_postings_{column}", "postings", [column])
    op.create_table(
        "observations",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False), sa.Column("subject_type", sa.String(30), nullable=False), sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("observation_type", sa.String(80), nullable=False), sa.Column("value_json", sa.Text(), nullable=False), sa.Column("source_reference_id", sa.String(36), sa.ForeignKey("source_references.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("confidence", sa.Float()), sa.Column("evidence_summary", sa.Text()), sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    for column in ("import_id", "subject_type", "subject_id"):
        op.create_index(f"ix_observations_{column}", "observations", [column])
    op.create_table(
        "external_assessments",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("import_id", sa.String(36), sa.ForeignKey("research_imports.id"), nullable=False),
        sa.Column("bundle_local_id", sa.String(200), nullable=False), sa.Column("subject_type", sa.String(30), nullable=False), sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("criterion_id", sa.String(100), sa.ForeignKey("assessment_criteria.criterion_id"), nullable=False), sa.Column("value_json", sa.Text(), nullable=False), sa.Column("origin", sa.String(30), nullable=False),
        sa.Column("source_reference_ids_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("reasoning", sa.Text()), sa.UniqueConstraint("import_id", "bundle_local_id"),
    )
    for column in ("import_id", "subject_type", "subject_id", "criterion_id"):
        op.create_index(f"ix_external_assessments_{column}", "external_assessments", [column])


def downgrade() -> None:
    for table in ("external_assessments", "observations", "postings", "work_locations", "opportunities", "companies", "source_references", "sources", "import_issues", "prompt_runs", "assessment_criteria", "research_imports"):
        op.drop_table(table)
