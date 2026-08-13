from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ValueType = Literal["numeric", "boolean", "categorical", "text"]
SubjectType = Literal["company", "opportunity", "posting"]
TrackingStatus = Literal["new", "to_review", "interesting", "shortlisted", "deferred", "excluded", "archived"]
GroupType = Literal["general", "application_wave"]
UpdateMode = Literal["full_update", "company_update", "opportunity_update", "gap_filling"]
ObservationType = Literal[
    "technology_requirement",
    "task",
    "seniority",
    "experience_requirement",
    "work_model",
    "salary",
]
BundleVersion = Literal["1.0", "2.0"]
PublishedPrecision = Literal["exact_address", "site", "city", "region", "approximate", "unknown"]
ApplicationLifecycle = Literal[
    "draft",
    "ready",
    "submitted",
    "interviewing",
    "offer",
    "accepted",
    "rejected",
    "withdrawn",
]
ApplicationMaterialKind = Literal["cv", "cover_letter", "other"]


class CriterionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=200)
    description: str = ""
    value_type: ValueType
    numeric_min: float | None = None
    numeric_max: float | None = None
    allowed_values: list[str] = Field(default_factory=list)
    applicable_subject_type: SubjectType
    active: bool = True
    display_order: int = Field(default=10, ge=0)

    @model_validator(mode="after")
    def value_configuration(self):
        if self.value_type == "numeric" and (self.numeric_min is None or self.numeric_max is None):
            raise ValueError("Numeric criteria require minimum and maximum values.")
        if self.value_type == "categorical" and not self.allowed_values:
            raise ValueError("Categorical criteria require allowed values.")
        return self


class CriterionResponse(CriterionPayload):
    revision: int


class ActivationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active: bool


class ReorderPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    criterion_ids: list[str]


class InitialPromptPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search_profile: str = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    as_of_date: date


class GeneratedPromptResponse(BaseModel):
    prompt_run_id: str
    prompt_text: str
    bundle_version: BundleVersion
    criteria_count: int


class PublishedCompanyResponse(BaseModel):
    company_ref: str
    name: str


class PublishedWorkLocationResponse(BaseModel):
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: PublishedPrecision


class PublishedOpportunityResponse(BaseModel):
    opportunity_ref: str
    title: str
    company: PublishedCompanyResponse
    work_locations: list[PublishedWorkLocationResponse]
    posting_count: int


class PublishedPublicationResponse(BaseModel):
    publication_ref: str
    generated_at: str


class PublishedOpportunityOverviewResponse(BaseModel):
    capability: Literal["vocation.opportunity_overview"]
    contract_version: Literal["1.0"]
    publication: PublishedPublicationResponse
    opportunities: list[PublishedOpportunityResponse]


class PublishedMapCompanyResponse(BaseModel):
    company_ref: str
    name: str


class PublishedMapWorkLocationResponse(BaseModel):
    label: str
    precision: PublishedPrecision


class PublishedMapCoordinatesResponse(BaseModel):
    latitude: float
    longitude: float


class PublishedMapFeatureResponse(BaseModel):
    feature_ref: str
    opportunity_ref: str
    title: str
    company: PublishedMapCompanyResponse
    work_location: PublishedMapWorkLocationResponse
    coordinates: PublishedMapCoordinatesResponse


class PublishedMapProjectionResponse(BaseModel):
    capability: Literal["vocation.map_projection"]
    contract_version: Literal["1.0"]
    publication: PublishedPublicationResponse
    features: list[PublishedMapFeatureResponse]


class CompanyOptionResponse(BaseModel):
    id: str
    name: str


class OpportunityOptionResponse(BaseModel):
    id: str
    company_id: str
    title: str


class PostingOptionResponse(BaseModel):
    id: str
    company_id: str
    opportunity_id: str
    title: str


class UpdatePromptOptionsResponse(BaseModel):
    companies: list[CompanyOptionResponse]
    opportunities: list[OpportunityOptionResponse]
    postings: list[PostingOptionResponse]
    observation_types: list[ObservationType]


class GapRequestPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_type: SubjectType
    subject_id: str = Field(min_length=1)
    observation_type: ObservationType | None = None
    criterion_id: str | None = None

    @model_validator(mode="after")
    def exactly_one_evidence_kind(self):
        if (self.observation_type is None) == (self.criterion_id is None):
            raise ValueError("Gap requests require exactly one of observation_type or criterion_id.")
        return self


class UpdatePromptPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: UpdateMode
    as_of_date: date
    selected_ids: list[str] = Field(default_factory=list)
    gap_requests: list[GapRequestPayload] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mode_shape(self):
        if self.mode == "full_update" and (self.selected_ids or self.gap_requests):
            raise ValueError("Full Update does not accept selected_ids or gap_requests.")
        if self.mode in {"company_update", "opportunity_update"}:
            if not self.selected_ids or len(self.selected_ids) != len(set(self.selected_ids)):
                raise ValueError("Selected IDs must be nonempty and unique.")
            if self.gap_requests:
                raise ValueError("This update mode does not accept gap_requests.")
        if self.mode == "gap_filling" and (self.selected_ids or not self.gap_requests):
            raise ValueError("Gap Filling requires gap_requests and no selected_ids.")
        return self


class GeneratedUpdatePromptResponse(BaseModel):
    prompt_run_id: str
    prompt_context_ref: str
    prompt_type: UpdateMode
    prompt_version: str
    bundle_version: Literal["2.0"]
    research_scope: ResearchScope
    prompt_text: str
    criteria_count: int


class AvailabilityPromptPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of_date: date
    posting_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_postings(self):
        if len(self.posting_ids) != len(set(self.posting_ids)):
            raise ValueError("Posting IDs must be unique.")
        return self


class GeneratedAvailabilityPromptResponse(BaseModel):
    prompt_run_id: str
    prompt_context_ref: str
    prompt_type: Literal["availability_check"]
    prompt_version: Literal["1.0"]
    bundle_kind: Literal["availability_check"]
    bundle_version: Literal["1.0"]
    research_scope: dict[str, Any]
    prompt_text: str


class AvailabilityImportTextPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str


class FullResearchScope(BaseModel):
    type: Literal["full_update"]
    as_of_date: str


class SelectedResearchScope(BaseModel):
    type: Literal["company_update", "opportunity_update"]
    as_of_date: str
    selected_correlation_refs: list[str]


class GapObservationScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_type: SubjectType
    correlation_ref: str
    observation_type: ObservationType
    criterion_id: None = None


class GapCriterionScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_type: SubjectType
    correlation_ref: str
    observation_type: None = None
    criterion_id: str


class GapResearchScope(BaseModel):
    type: Literal["gap_filling"]
    as_of_date: str
    selected_correlation_refs: list[str]
    requests: list[Annotated[GapObservationScopeRequest | GapCriterionScopeRequest, Field(union_mode="left_to_right")]]


ResearchScope = Annotated[
    FullResearchScope | SelectedResearchScope | GapResearchScope,
    Field(discriminator="type"),
]


class ImportTextPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str


class ImportIssueResponse(BaseModel):
    severity: str
    code: str
    path: str
    message: str


class AvailabilityImportReportResponse(BaseModel):
    import_id: str
    import_kind: Literal["availability_check"]
    status: str
    bundle_id: str | None
    fingerprint: str | None
    counts: dict[str, int]
    warnings: list[str]
    issues: list[ImportIssueResponse]
    duplicate_of_import_id: str | None = None
    bundle_version: str | None = None
    prompt_context_ref: str | None = None


class ImportReportResponse(BaseModel):
    import_id: str
    status: str
    bundle_id: str | None
    fingerprint: str | None
    counts: dict[str, int]
    warnings: list[str]
    issues: list[ImportIssueResponse]
    duplicate_of_import_id: str | None = None
    bundle_version: str | None = None
    prompt_context_ref: str | None = None


class OpportunityListItemResponse(BaseModel):
    id: str
    title: str
    company_name: str
    locations: list[str]
    posting_count: int
    assessment_count: int
    import_id: str
    imported_at: str
    tracking_status: TrackingStatus
    availability: Literal["available", "unavailable", "uncertain", "unknown"] | None = None
    availability_last_checked_at: str | None = None
    availability_age_days: int | None = None
    groups: list[OpportunityGroupSummaryResponse] = Field(default_factory=list)


class CompanyResponse(BaseModel):
    id: str
    name: str


class LocationResponse(BaseModel):
    label: str
    precision: str
    evidence_summary: str | None


class SourceResponse(BaseModel):
    id: str
    name: str
    type: str
    base_url: str | None = None


class SourceReferenceResponse(BaseModel):
    id: str
    url: str
    display_label: str | None
    observed_at: str


class PostingResponse(BaseModel):
    id: str
    title: str
    published_at: str | None
    observed_at: str
    source: SourceResponse
    source_reference: SourceReferenceResponse
    availability: Literal["available", "unavailable", "uncertain", "unknown"] | None = None
    availability_last_checked_at: str | None = None
    availability_age_days: int | None = None
    availability_history: list[AvailabilityHistoryResponse] = Field(default_factory=list)


class AvailabilityHistoryResponse(BaseModel):
    id: str
    import_id: str
    result: str
    observed_at: str
    recorded_at: str
    evidence_summary: str


class GroupMembershipResponse(BaseModel):
    opportunity_id: str
    position: int
    opportunity_title: str
    company_name: str


class OpportunityGroupPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    group_type: GroupType


class OpportunityGroupMembershipPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str = Field(min_length=1)


class OpportunityGroupReorderPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_ids: list[str]


class OpportunityGroupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    group_type: GroupType
    memberships: list[GroupMembershipResponse]


class OpportunityGroupSummaryResponse(BaseModel):
    group_id: str
    name: str
    group_type: GroupType


class ApplicationLifecycleEventResponse(BaseModel):
    previous_status: ApplicationLifecycle | None
    resulting_status: ApplicationLifecycle
    occurred_at: datetime


class ApplicationCaseResponse(BaseModel):
    id: str
    opportunity_id: str
    lifecycle: ApplicationLifecycle
    created_at: datetime
    updated_at: datetime
    lifecycle_events: list[ApplicationLifecycleEventResponse]


class ApplicationMaterialResponse(BaseModel):
    id: str
    application_case_id: str
    kind: ApplicationMaterialKind
    display_name: str
    revision: int
    created_at: datetime
    updated_at: datetime


class ApplicationDocumentResponse(BaseModel):
    id: str
    material_id: str
    material_revision: int
    original_filename: str
    media_type: Literal["application/pdf", "text/plain", "text/markdown"]
    byte_size: int
    sha256: str
    created_at: datetime


class ApplicationCaseLifecyclePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lifecycle: ApplicationLifecycle


class ApplicationMaterialPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: ApplicationMaterialKind
    display_name: str = Field(min_length=1)


class ApplicationMaterialRevisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1)


class MapResolutionResponse(BaseModel):
    latitude: float
    longitude: float
    resolution_source: Literal["manual", "geocoder"]
    provider_key: str | None
    resolved_at: str
    resolved_query: str


class MapLocationResponse(BaseModel):
    work_location_id: str
    opportunity_id: str
    title: str
    company_id: str
    company_name: str
    label: str
    city: str | None
    region: str | None
    country_code: str | None
    precision: str
    resolution: MapResolutionResponse | None


class ExternalLinkResponse(BaseModel):
    posting_id: str
    source_id: str
    source_name: str
    source_type: Literal["company_careers", "job_board", "professional_network", "other"]
    url: str
    display_label: str | None
    availability: Literal["available", "unavailable", "uncertain", "unknown"]
    observed_at: str
    preferred: bool


class ExternalLinkOpenPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    posting_id: str | None = None


class MapResolutionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float
    longitude: float
    resolved_query: str = Field(min_length=1)


class GeocodeResolutionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)


class MapProjectionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_ids: list[str] = Field(default_factory=list)


class MapGroupMembershipResponse(BaseModel):
    group_id: str
    name: str
    group_type: GroupType


class MapProjectionFeatureResponse(BaseModel):
    feature_id: str
    work_location_id: str
    opportunity_id: str
    company_id: str
    title: str
    company_name: str
    location_label: str
    latitude: float
    longitude: float
    precision: str
    tracking_status: TrackingStatus
    availability: Literal["available", "unavailable", "uncertain", "unknown"]
    groups: list[MapGroupMembershipResponse]


class ComparisonWorkLocationResponse(BaseModel):
    label: str
    precision: str


class ComparisonDimensionValueResponse(BaseModel):
    value: Any
    subject_type: Literal["opportunity", "posting"]
    subject_id: str
    observed_at: str
    evidence_summary: str | None


class ComparisonDimensionCellResponse(BaseModel):
    state: Literal["present", "missing"]
    values: list[ComparisonDimensionValueResponse]


class ComparisonAssessmentCriterionResponse(BaseModel):
    criterion_id: str
    display_name: str
    display_order: int


class ComparisonPersonalAssessmentResponse(BaseModel):
    criterion_id: str
    value: Any
    reasoning: str | None
    created_at: str


class ComparisonExternalAssessmentResponse(BaseModel):
    criterion_id: str
    value: Any
    reasoning: str | None
    created_at: str


class ComparisonOpportunityResponse(BaseModel):
    opportunity_id: str
    title: str
    company_id: str
    company_name: str
    work_locations: list[ComparisonWorkLocationResponse]
    tracking_status: TrackingStatus
    availability: Literal["available", "unavailable", "uncertain", "unknown"]
    availability_last_checked_at: str | None
    availability_age_days: int | None
    groups: list[MapGroupMembershipResponse]
    research_dimensions: dict[str, ComparisonDimensionCellResponse]
    personal_assessments: list[ComparisonPersonalAssessmentResponse]
    external_assessments: list[ComparisonExternalAssessmentResponse]


class OpportunityComparisonResponse(BaseModel):
    opportunities: list[ComparisonOpportunityResponse]
    assessment_criteria: list[ComparisonAssessmentCriterionResponse]


class OpportunityComparisonPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_ids: list[str]


class ObservationResponse(BaseModel):
    id: str
    subject_type: str
    type: str
    value: Any
    observed_at: str
    confidence: float | None
    evidence_summary: str | None


class AssessmentResponse(BaseModel):
    id: str
    criterion_id: str
    criterion_name: str
    value: Any
    origin: str
    reasoning: str | None


class PersonalAssessmentResponse(BaseModel):
    id: str
    opportunity_id: str
    criterion_id: str
    criterion_name: str
    value: Any
    reasoning: str | None
    created_at: str
    supersedes_id: str | None
    revision_number: int
    origin: str


class DecisionResponse(BaseModel):
    id: str
    opportunity_id: str
    decision_type: str
    previous_status: TrackingStatus
    resulting_status: TrackingStatus
    reason: str | None
    created_at: str
    reverses_decision_id: str | None


class PersonalAssessmentPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    criterion_id: str = Field(min_length=1)
    value: Any
    reasoning: str | None = None


class PersonalAssessmentRevisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: Any
    reasoning: str | None = None


class StatusPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: TrackingStatus
    reason: str | None = None


class ExclusionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(min_length=1)


class RestorePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_status: TrackingStatus | None = None
    reason: str | None = None


class ImportProvenanceResponse(BaseModel):
    import_id: str
    bundle_id: str
    fingerprint: str
    applied_at: str


class OpportunityDetailResponse(BaseModel):
    id: str
    title: str
    company: CompanyResponse
    locations: list[LocationResponse]
    postings: list[PostingResponse]
    sources: list[SourceResponse]
    observations: list[ObservationResponse]
    tracking_status: TrackingStatus
    external_assessments: list[AssessmentResponse]
    assessments: list[AssessmentResponse]
    personal_assessments: list[PersonalAssessmentResponse]
    personal_assessment_history: list[PersonalAssessmentResponse]
    decision_history: list[DecisionResponse]
    import_provenance: ImportProvenanceResponse
    availability: Literal["available", "unavailable", "uncertain", "unknown"] | None = None
    availability_last_checked_at: str | None = None
    availability_age_days: int | None = None
    groups: list[OpportunityGroupSummaryResponse] = Field(default_factory=list)
