from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ValueType = Literal["numeric", "boolean", "categorical", "text"]
SubjectType = Literal["company", "opportunity", "posting"]


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
