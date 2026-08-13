from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class ResearchImportModel(Base):
    __tablename__ = "research_imports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bundle_id: Mapped[str | None] = mapped_column(String(200))
    bundle_version: Mapped[str | None] = mapped_column(String(20))
    import_kind: Mapped[str] = mapped_column(String(30), nullable=False, default="research", server_default="research")
    fingerprint: Mapped[str | None] = mapped_column(String(64), index=True)
    prompt_context_ref: Mapped[str | None] = mapped_column(
        ForeignKey("prompt_context_snapshots.prompt_context_ref", name="fk_research_imports_prompt_context_ref"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    counts_json: Mapped[str] = mapped_column(Text, default="{}")
    warnings_json: Mapped[str] = mapped_column(Text, default="[]")

    issues: Mapped[list[ImportIssueModel]] = relationship(back_populates="research_import", cascade="all, delete-orphan")
    duplicate_cases: Mapped[list[DuplicateCaseModel]] = relationship(back_populates="research_import")
    prompt_context_snapshot: Mapped[PromptContextSnapshotModel | None] = relationship(back_populates="research_imports")
    availability_observations: Mapped[list[AvailabilityObservationModel]] = relationship(back_populates="research_import")


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
    search_profile: Mapped[str | None] = mapped_column(Text)
    prompt_context_ref: Mapped[str | None] = mapped_column(
        ForeignKey("prompt_context_snapshots.prompt_context_ref", name="fk_prompt_runs_prompt_context_ref")
    )
    constraints_json: Mapped[str] = mapped_column(Text)
    as_of_date: Mapped[str] = mapped_column(String(10))
    criteria_snapshot_json: Mapped[str] = mapped_column(Text)
    prompt_text: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    prompt_context_snapshot: Mapped[PromptContextSnapshotModel | None] = relationship(back_populates="prompt_run")
    __table_args__ = (UniqueConstraint("prompt_context_ref", name="uq_prompt_runs_prompt_context_ref"),)


class PromptContextSnapshotModel(Base):
    __tablename__ = "prompt_context_snapshots"

    prompt_context_ref: Mapped[str] = mapped_column(String(200), primary_key=True)
    scope_type: Mapped[str] = mapped_column(String(30), nullable=False)
    as_of_date: Mapped[str] = mapped_column(String(10), nullable=False)
    scope_json: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    subjects: Mapped[list[PromptContextSubjectModel]] = relationship(back_populates="prompt_context_snapshot", cascade="all, delete-orphan")
    prompt_run: Mapped[PromptRunModel | None] = relationship(back_populates="prompt_context_snapshot")
    research_imports: Mapped[list[ResearchImportModel]] = relationship(back_populates="prompt_context_snapshot")
    __table_args__ = (
        CheckConstraint(
            "scope_type IN ('full_update','company_update','opportunity_update','gap_filling','availability_check')",
            name="ck_prompt_context_snapshot_scope_type",
        ),
        CheckConstraint("length(prompt_context_ref) > 0 AND length(prompt_context_ref) <= 200", name="ck_prompt_context_ref_length"),
        CheckConstraint("length(fingerprint) = 64", name="ck_prompt_context_fingerprint_length"),
    )


class PromptContextSubjectModel(Base):
    __tablename__ = "prompt_context_subjects"

    prompt_context_ref: Mapped[str] = mapped_column(
        ForeignKey("prompt_context_snapshots.prompt_context_ref", ondelete="CASCADE"), primary_key=True
    )
    correlation_ref: Mapped[str] = mapped_column(String(200), primary_key=True)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_target: Mapped[bool] = mapped_column(Boolean, nullable=False)

    prompt_context_snapshot: Mapped[PromptContextSnapshotModel] = relationship(back_populates="subjects")
    __table_args__ = (
        UniqueConstraint(
            "prompt_context_ref",
            "subject_type",
            "subject_id",
            name="uq_prompt_context_subject_subject",
        ),
        CheckConstraint("subject_type IN ('company','opportunity','posting')", name="ck_prompt_context_subject_type"),
        CheckConstraint("length(correlation_ref) > 0 AND length(correlation_ref) <= 200", name="ck_prompt_context_correlation_ref_length"),
    )


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
    duplicate_case_links: Mapped[list[DuplicateCaseSourceReferenceModel]] = relationship(back_populates="source_reference")
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
    group_memberships: Mapped[list[OpportunityGroupMembershipModel]] = relationship(back_populates="opportunity")
    application_cases: Mapped[list[ApplicationCaseModel]] = relationship(back_populates="opportunity")


class ApplicationCaseModel(Base):
    __tablename__ = "application_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id"), nullable=False, index=True)
    lifecycle: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    opportunity: Mapped[OpportunityModel] = relationship(back_populates="application_cases")
    lifecycle_events: Mapped[list[ApplicationCaseLifecycleEventModel]] = relationship(
        back_populates="application_case",
        cascade="all, delete-orphan",
        order_by="ApplicationCaseLifecycleEventModel.sequence",
    )
    materials: Mapped[list[ApplicationMaterialModel]] = relationship(
        back_populates="application_case",
        cascade="all, delete-orphan",
    )
    __table_args__ = (
        CheckConstraint(
            "lifecycle IN ('draft','ready','submitted','interviewing','offer','accepted','rejected','withdrawn')",
            name="ck_application_cases_lifecycle",
        ),
        Index(
            "uq_application_cases_one_active_per_opportunity",
            "opportunity_id",
            unique=True,
            sqlite_where=text("lifecycle NOT IN ('accepted','rejected','withdrawn')"),
        ),
    )


class ApplicationCaseLifecycleEventModel(Base):
    __tablename__ = "application_case_lifecycle_events"

    application_case_id: Mapped[str] = mapped_column(ForeignKey("application_cases.id", ondelete="CASCADE"), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    previous_status: Mapped[str | None] = mapped_column(String(30))
    resulting_status: Mapped[str] = mapped_column(String(30), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    application_case: Mapped[ApplicationCaseModel] = relationship(back_populates="lifecycle_events")
    __table_args__ = (
        CheckConstraint("sequence >= 1", name="ck_application_case_lifecycle_events_sequence"),
        CheckConstraint(
            "previous_status IS NULL OR previous_status IN "
            "('draft','ready','submitted','interviewing','offer','accepted','rejected','withdrawn')",
            name="ck_application_case_lifecycle_events_previous_status",
        ),
        CheckConstraint(
            "resulting_status IN ('draft','ready','submitted','interviewing','offer','accepted','rejected','withdrawn')",
            name="ck_application_case_lifecycle_events_resulting_status",
        ),
    )


class ApplicationMaterialModel(Base):
    __tablename__ = "application_materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    application_case_id: Mapped[str] = mapped_column(ForeignKey("application_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    application_case: Mapped[ApplicationCaseModel] = relationship(back_populates="materials")
    revisions: Mapped[list[ApplicationMaterialRevisionModel]] = relationship(
        back_populates="material",
        cascade="all, delete-orphan",
        order_by="ApplicationMaterialRevisionModel.revision",
    )
    __table_args__ = (CheckConstraint("kind IN ('cv','cover_letter','other')", name="ck_application_materials_kind"),)


class ApplicationMaterialRevisionModel(Base):
    __tablename__ = "application_material_revisions"

    material_id: Mapped[str] = mapped_column(ForeignKey("application_materials.id", ondelete="CASCADE"), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(300), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    material: Mapped[ApplicationMaterialModel] = relationship(back_populates="revisions")
    documents: Mapped[list[ApplicationDocumentModel]] = relationship(back_populates="material_revision")
    __table_args__ = (
        CheckConstraint("revision >= 1", name="ck_application_material_revisions_revision"),
        CheckConstraint(
            "length(trim(display_name)) > 0",
            name="ck_application_material_revisions_display_name_nonempty",
        ),
    )


class ApplicationDocumentModel(Base):
    __tablename__ = "application_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    material_id: Mapped[str] = mapped_column(String(36), nullable=False)
    material_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(300), nullable=False)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    material_revision_record: Mapped[ApplicationMaterialRevisionModel] = relationship(back_populates="documents")
    __table_args__ = (
        ForeignKeyConstraint(
            ["material_id", "material_revision"],
            ["application_material_revisions.material_id", "application_material_revisions.revision"],
            name="fk_application_documents_material_revision",
        ),
        UniqueConstraint("material_id", "material_revision", name="uq_application_documents_material_revision"),
        CheckConstraint("material_revision >= 1", name="ck_application_documents_material_revision"),
        CheckConstraint("byte_size >= 0", name="ck_application_documents_byte_size"),
        CheckConstraint("length(trim(original_filename)) > 0", name="ck_application_documents_filename_nonempty"),
        CheckConstraint("length(trim(storage_ref)) > 0", name="ck_application_documents_storage_ref_nonempty"),
        CheckConstraint(
            "media_type IN ('application/pdf','text/plain','text/markdown')",
            name="ck_application_documents_media_type",
        ),
        CheckConstraint(
            "length(sha256) = 64 AND sha256 = lower(sha256) AND sha256 NOT GLOB '*[^0-9a-f]*'",
            name="ck_application_documents_sha256",
        ),
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
    map_location_resolution: Mapped[MapLocationResolutionModel | None] = relationship(
        back_populates="work_location", cascade="all, delete-orphan", uselist=False
    )


class MapLocationResolutionModel(Base):
    __tablename__ = "map_location_resolutions"

    work_location_id: Mapped[str] = mapped_column(ForeignKey("work_locations.id", ondelete="CASCADE"), primary_key=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    resolution_source: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_key: Mapped[str | None] = mapped_column(String(200))
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_query: Mapped[str] = mapped_column(Text, nullable=False)

    work_location: Mapped[WorkLocationModel] = relationship(back_populates="map_location_resolution")
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_map_location_resolutions_latitude"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_map_location_resolutions_longitude"),
        CheckConstraint("resolution_source IN ('manual','geocoder')", name="ck_map_location_resolutions_source"),
        CheckConstraint("length(trim(resolved_query)) > 0", name="ck_map_location_resolutions_query_nonempty"),
        CheckConstraint(
            "(resolution_source = 'manual' AND provider_key IS NULL) "
            "OR (resolution_source = 'geocoder' AND length(trim(provider_key)) > 0)",
            name="ck_map_location_resolutions_provider",
        ),
    )


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
    availability_observations: Mapped[list[AvailabilityObservationModel]] = relationship(back_populates="posting")
    __table_args__ = (UniqueConstraint("import_id", "bundle_local_id"),)


class AvailabilityObservationModel(Base):
    __tablename__ = "availability_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    bundle_local_id: Mapped[str] = mapped_column(String(200))
    posting_id: Mapped[str] = mapped_column(ForeignKey("postings.id"), index=True)
    result: Mapped[str] = mapped_column(String(40))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    evidence_summary: Mapped[str] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    research_import: Mapped[ResearchImportModel] = relationship(back_populates="availability_observations")
    posting: Mapped[PostingModel] = relationship(back_populates="availability_observations")
    __table_args__ = (
        UniqueConstraint("import_id", "bundle_local_id"),
        UniqueConstraint("import_id", "posting_id"),
        CheckConstraint(
            "result IN ('explicitly_available','explicitly_unavailable','temporarily_unreachable','not_found','indeterminate')",
        ),
        CheckConstraint("length(trim(evidence_summary)) > 0"),
    )


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


class OpportunityGroupModel(Base):
    __tablename__ = "opportunity_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    group_type: Mapped[str] = mapped_column(String(30), nullable=False)

    memberships: Mapped[list[OpportunityGroupMembershipModel]] = relationship(
        back_populates="group", cascade="all, delete-orphan", order_by="OpportunityGroupMembershipModel.position"
    )
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_opportunity_groups_name_nonempty"),
        CheckConstraint("group_type IN ('general','application_wave')", name="ck_opportunity_groups_group_type"),
    )


class OpportunityGroupMembershipModel(Base):
    __tablename__ = "opportunity_group_memberships"

    group_id: Mapped[str] = mapped_column(ForeignKey("opportunity_groups.id", ondelete="CASCADE"), primary_key=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id"), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    group: Mapped[OpportunityGroupModel] = relationship(back_populates="memberships")
    opportunity: Mapped[OpportunityModel] = relationship(back_populates="group_memberships")
    __table_args__ = (
        UniqueConstraint("group_id", "position", name="uq_opportunity_group_memberships_position"),
        CheckConstraint("position >= 0", name="ck_opportunity_group_memberships_position_nonnegative"),
    )


class DuplicateCaseModel(Base):
    __tablename__ = "duplicate_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    research_import_id: Mapped[str] = mapped_column(ForeignKey("research_imports.id"), index=True)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    left_subject_id: Mapped[str] = mapped_column(String(36), nullable=False)
    right_subject_id: Mapped[str] = mapped_column(String(36), nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    research_import: Mapped[ResearchImportModel] = relationship(back_populates="duplicate_cases")
    source_reference_links: Mapped[list[DuplicateCaseSourceReferenceModel]] = relationship(
        back_populates="duplicate_case", cascade="all, delete-orphan"
    )
    __table_args__ = (
        UniqueConstraint("subject_type", "left_subject_id", "right_subject_id", name="uq_duplicate_case_subject_pair"),
        CheckConstraint("subject_type IN ('opportunity','posting')", name="ck_duplicate_case_subject_type"),
        CheckConstraint("left_subject_id <> right_subject_id", name="ck_duplicate_case_distinct_subjects"),
        CheckConstraint("length(trim(evidence_summary)) > 0", name="ck_duplicate_case_evidence_nonempty"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_duplicate_case_confidence_range"),
    )


class DuplicateCaseSourceReferenceModel(Base):
    __tablename__ = "duplicate_case_source_references"

    duplicate_case_id: Mapped[str] = mapped_column(ForeignKey("duplicate_cases.id", ondelete="CASCADE"), primary_key=True)
    source_reference_id: Mapped[str] = mapped_column(ForeignKey("source_references.id"), primary_key=True)

    duplicate_case: Mapped[DuplicateCaseModel] = relationship(back_populates="source_reference_links")
    source_reference: Mapped[SourceReferenceModel] = relationship(back_populates="duplicate_case_links")
