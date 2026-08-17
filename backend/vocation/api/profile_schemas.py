from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SkillLevel = Literal["learning", "basic", "working", "strong", "expert"]
WorkModel = Literal["remote", "hybrid", "on_site"]
NumericDirection = Literal["higher_is_better", "lower_is_better"]


class EducationPayload(BaseModel):
    degree: str
    field: str
    institution: str
    status: str = "completed"
    graduation_year: int | None = None


class SkillPayload(BaseModel):
    name: str
    level: SkillLevel
    notes: str | None = None


class LanguagePayload(BaseModel):
    name: str
    level: str


class ProjectHighlightPayload(BaseModel):
    name: str
    summary: str
    technologies: list[str] = Field(default_factory=list)


class CandidateProfilePayload(BaseModel):
    headline: str
    summary: str
    education: list[EducationPayload] = Field(default_factory=list)
    skills: list[SkillPayload] = Field(default_factory=list)
    languages: list[LanguagePayload] = Field(default_factory=list)
    experience_summary: str = ""
    projects: list[ProjectHighlightPayload] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class CandidateProfileResponse(CandidateProfilePayload):
    revision: int


class CategoryScorePayload(BaseModel):
    value: str
    score: float


class CriterionPolicyPayload(BaseModel):
    criterion_id: str
    weight: float = 1.0
    required: bool = False
    numeric_direction: NumericDirection = "higher_is_better"
    minimum_numeric_value: float | None = None
    minimum_score: float | None = None
    preferred_boolean: bool | None = None
    category_scores: list[CategoryScorePayload] = Field(default_factory=list)


class SearchProfilePayload(BaseModel):
    name: str
    description: str
    target_roles: list[str]
    seniority_targets: list[str] = Field(default_factory=list)
    preferred_technologies: list[str] = Field(default_factory=list)
    acceptable_technologies: list[str] = Field(default_factory=list)
    avoided_technologies: list[str] = Field(default_factory=list)
    target_locations: list[str] = Field(default_factory=list)
    work_models: list[WorkModel] = Field(default_factory=list)
    relocation_willing: bool = False
    employment_types: list[str] = Field(default_factory=list)
    preferred_industries: list[str] = Field(default_factory=list)
    avoided_industries: list[str] = Field(default_factory=list)
    preferred_company_characteristics: list[str] = Field(default_factory=list)
    avoided_company_characteristics: list[str] = Field(default_factory=list)
    salary_floor: int | None = None
    salary_target: int | None = None
    salary_currency: str = "EUR"
    must_haves: list[str] = Field(default_factory=list)
    must_not_haves: list[str] = Field(default_factory=list)
    result_limit: int = 12
    criterion_policies: list[CriterionPolicyPayload] = Field(default_factory=list)


class SearchProfileResponse(SearchProfilePayload):
    id: str
    revision: int
    is_default: bool
