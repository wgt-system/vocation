from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class ResearchImportModel(Base):
    __tablename__ = "research_imports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bundle_id: Mapped[str | None] = mapped_column(String(200))
    fingerprint: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    counts_json: Mapped[str] = mapped_column(Text, default="{}")
    warnings_json: Mapped[str] = mapped_column(Text, default="[]")

    issues: Mapped[list[ImportIssueModel]] = relationship(back_populates="research_import", cascade="all, delete-orphan")


class ImportIssueModel(Base):
    __tablename__ = "import_issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id", ondelete="CASCADE"), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(80))
    path: Mapped[str] = mapped_column(String(500), default="$")
    message: Mapped[str] = mapped_column(Text)

    research_import: Mapped[ResearchImportModel] = relationship(back_populates="issues")


class AssessmentCriterionModel(Base):
    __tablename__ = "assessment_criteria"

    criterion_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(30))
    numeric_min: Mapped[float | None] = mapped_column(Float)
    numeric_max: Mapped[float | None] = mapped_column(Float)
    allowed_values_json: Mapped[str] = mapped_column(Text, default="[]")
    applicable_subject_type: Mapped[str] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class PromptRunModel(Base):
    __tablename__ = "prompt_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt_type: Mapped[str] = mapped_column(String(50), default="initial_market_research")
    prompt_version: Mapped[str] = mapped_column(String(20), default="1.0")
    bundle_version: Mapped[str] = mapped_column(String(20), default="1.0")
    search_profile: Mapped[str] = mapped_column(Text)
    constraints_json: Mapped[str] = mapped_column(Text)
    as_of_date: Mapped[str] = mapped_column(String(10))
    criteria_snapshot_json: Mapped[str] = mapped_column(Text)
    prompt_text: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(300))
    source_type: Mapped[str] = mapped_column(String(50))
    base_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    references: Mapped[list[SourceReferenceModel]] = relationship(back_populates="source")
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class SourceReferenceModel(Base):
    __tablename__ = "source_references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    url: Mapped[str] = mapped_column(Text)
    normalized_url: Mapped[str] = mapped_column(Text, index=True)
    external_reference_id: Mapped[str | None] = mapped_column(String(300))
    display_label: Mapped[str | None] = mapped_column(String(300))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    source: Mapped[SourceModel] = relationship(back_populates="references")
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    canonical_name: Mapped[str] = mapped_column(String(300), index=True)
    alternative_names_json: Mapped[str] = mapped_column(Text, default="[]")
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evidence_summary: Mapped[str | None] = mapped_column(Text)

    opportunities: Mapped[list[OpportunityModel]] = relationship(back_populates="company")
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True)
    canonical_title: Mapped[str] = mapped_column(String(300), index=True)
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evidence_summary: Mapped[str | None] = mapped_column(Text)
    tracking_status: Mapped[str] = mapped_column(String(30), nullable=False, default="new", server_default="new", index=True)

    company: Mapped[CompanyModel] = relationship(back_populates="opportunities")
    locations: Mapped[list[WorkLocationModel]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    postings: Mapped[list[PostingModel]] = relationship(back_populates="opportunity")
    __table_args__ = (
        UniqueConstraint("import_id", "bundle_local_id"),
        CheckConstraint("tracking_status IN ('new','to_review','interesting','shortlisted','deferred','excluded','archived')"),
    )


class WorkLocationModel(Base):
    __tablename__ = "work_locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(200))
    region: Mapped[str | None] = mapped_column(String(200))
    country_code: Mapped[str | None] = mapped_column(String(2))
    precision: Mapped[str] = mapped_column(String(30))
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    evidence_summary: Mapped[str | None] = mapped_column(Text)

    opportunity: Mapped[OpportunityModel] = relationship(back_populates="locations")


class PostingModel(Base):
    __tablename__ = "postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id"), index=True)
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"))
    title: Mapped[str] = mapped_column(String(300))
    external_posting_id: Mapped[str | None] = mapped_column(String(300))
    stable_key: Mapped[str] = mapped_column(Text, unique=True)
    canonical_url: Mapped[str] = mapped_column(Text, unique=True)
    published_at: Mapped[str | None] = mapped_column(String(10))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_fingerprint: Mapped[str | None] = mapped_column(String(200))

    opportunity: Mapped[OpportunityModel] = relationship(back_populates="postings")
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class ObservationModel(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    subject_type: Mapped[str] = mapped_column(String(30), index=True)
    subject_id: Mapped[str] = mapped_column(String(36), index=True)
    observation_type: Mapped[str] = mapped_column(String(80))
    value_json: Mapped[str] = mapped_column(Text)
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence_summary: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class ExternalAssessmentModel(Base):
    __tablename__ = "external_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    subject_type: Mapped[str] = mapped_column(String(30), index=True)
    subject_id: Mapped[str] = mapped_column(String(36), index=True)
    criterion_id: Mapped[str] = mapped_column(ForeignKey("assessment_criteria.criterion_id"), index=True)
    value_json: Mapped[str] = mapped_column(Text)
    origin: Mapped[str] = mapped_column(String(30), default="external_research")
    source_reference_ids_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reasoning: Mapped[str | None] = mapped_column(Text)

    criterion: Mapped[AssessmentCriterionModel] = relationship()
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class PersonalAssessmentModel(Base):
    __tablename__ = "personal_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    criterion_id: Mapped[str] = mapped_column(ForeignKey("assessment_criteria.criterion_id"), index=True)
    value_json: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    supersedes_id: Mapped[str | None] = mapped_column(ForeignKey("personal_assessments.id"), index=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    origin: Mapped[str] = mapped_column(String(30), default="personal", nullable=False)

    criterion: Mapped[AssessmentCriterionModel] = relationship()
    __table_args__ = (
        UniqueConstraint("opportunity_id", "criterion_id", "revision_number"),
        UniqueConstraint("supersedes_id"),
        CheckConstraint("revision_number >= 1"),
        CheckConstraint("origin = 'personal'"),
    )


class OpportunityDecisionModel(Base):
    __tablename__ = "opportunity_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    decision_type: Mapped[str] = mapped_column(String(30), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(30), nullable=False)
    resulting_status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    reverses_decision_id: Mapped[str | None] = mapped_column(ForeignKey("opportunity_decisions.id"), index=True)

    __table_args__ = (
        CheckConstraint("decision_type IN ('status_change','exclusion','restore')"),
        CheckConstraint("previous_status IN ('new','to_review','interesting','shortlisted','deferred','excluded','archived')"),
        CheckConstraint("resulting_status IN ('new','to_review','interesting','shortlisted','deferred','excluded','archived')"),
        UniqueConstraint("reverses_decision_id"),
    )
