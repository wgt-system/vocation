from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ValueType = Literal["numeric", "boolean", "categorical", "text"]
SubjectType = Literal["company", "opportunity", "posting"]
TrackingStatus = Literal["new", "to_review", "interesting", "shortlisted", "deferred", "excluded", "archived"]


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
    bundle_version: str
    criteria_count: int


class ImportTextPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str


class ImportIssueResponse(BaseModel):
    severity: str
    code: str
    path: str
    message: str


class ImportReportResponse(BaseModel):
    import_id: str
    status: str
    bundle_id: str | None
    fingerprint: str | None
    counts: dict[str, int]
    warnings: list[str]
    issues: list[ImportIssueResponse]
    duplicate_of_import_id: str | None = None


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
