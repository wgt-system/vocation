from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SkillLevel = Literal["learning", "basic", "working", "strong", "expert"]
WorkModel = Literal["remote", "hybrid", "on_site"]


class ProfileValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Education:
    degree: str
    field: str
    institution: str
    status: str = "completed"
    graduation_year: int | None = None


@dataclass(frozen=True)
class Skill:
    name: str
    level: SkillLevel
    notes: str | None = None


@dataclass(frozen=True)
class Language:
    name: str
    level: str


@dataclass(frozen=True)
class ProjectHighlight:
    name: str
    summary: str
    technologies: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateProfile:
    revision: int
    headline: str
    summary: str
    education: tuple[Education, ...] = ()
    skills: tuple[Skill, ...] = ()
    languages: tuple[Language, ...] = ()
    experience_summary: str = ""
    projects: tuple[ProjectHighlight, ...] = ()
    interests: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchProfile:
    id: str
    revision: int
    name: str
    description: str
    target_roles: tuple[str, ...]
    seniority_targets: tuple[str, ...] = ()
    preferred_technologies: tuple[str, ...] = ()
    acceptable_technologies: tuple[str, ...] = ()
    avoided_technologies: tuple[str, ...] = ()
    target_locations: tuple[str, ...] = ()
    work_models: tuple[WorkModel, ...] = ()
    relocation_willing: bool = False
    employment_types: tuple[str, ...] = ()
    preferred_industries: tuple[str, ...] = ()
    avoided_industries: tuple[str, ...] = ()
    preferred_company_characteristics: tuple[str, ...] = ()
    avoided_company_characteristics: tuple[str, ...] = ()
    salary_floor: int | None = None
    salary_target: int | None = None
    salary_currency: str = "EUR"
    must_haves: tuple[str, ...] = ()
    must_not_haves: tuple[str, ...] = ()
    result_limit: int = 12
    is_default: bool = False


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ProfileValidationError(f"{label} must be non-empty.")


def _require_unique_nonempty(values: tuple[str, ...], label: str) -> None:
    normalized = [value.strip().casefold() for value in values]
    if any(not value for value in normalized):
        raise ProfileValidationError(f"{label} must not contain empty values.")
    if len(normalized) != len(set(normalized)):
        raise ProfileValidationError(f"{label} must contain unique values.")


def validate_candidate_profile(profile: CandidateProfile) -> None:
    if profile.revision < 1:
        raise ProfileValidationError("Candidate Profile revision must be at least 1.")
    _require_text(profile.headline, "Candidate Profile headline")
    _require_text(profile.summary, "Candidate Profile summary")
    _require_unique_nonempty(profile.interests, "Candidate Profile interests")

    skill_names: list[str] = []
    for skill in profile.skills:
        _require_text(skill.name, "Skill name")
        if skill.level not in {"learning", "basic", "working", "strong", "expert"}:
            raise ProfileValidationError(f"Unsupported skill level: {skill.level}")
        skill_names.append(skill.name.strip().casefold())
    if len(skill_names) != len(set(skill_names)):
        raise ProfileValidationError("Candidate Profile skills must have unique names.")

    language_names: list[str] = []
    for language in profile.languages:
        _require_text(language.name, "Language name")
        _require_text(language.level, "Language level")
        language_names.append(language.name.strip().casefold())
    if len(language_names) != len(set(language_names)):
        raise ProfileValidationError("Candidate Profile languages must have unique names.")

    for education in profile.education:
        _require_text(education.degree, "Education degree")
        _require_text(education.field, "Education field")
        _require_text(education.institution, "Education institution")
        _require_text(education.status, "Education status")
        if education.graduation_year is not None and not 1900 <= education.graduation_year <= 2200:
            raise ProfileValidationError("Education graduation year is invalid.")

    project_names: list[str] = []
    for project in profile.projects:
        _require_text(project.name, "Project name")
        _require_text(project.summary, "Project summary")
        _require_unique_nonempty(project.technologies, f"Technologies for project '{project.name}'")
        project_names.append(project.name.strip().casefold())
    if len(project_names) != len(set(project_names)):
        raise ProfileValidationError("Candidate Profile projects must have unique names.")


def validate_search_profile(profile: SearchProfile) -> None:
    if profile.revision < 1:
        raise ProfileValidationError("Search Profile revision must be at least 1.")
    _require_text(profile.name, "Search Profile name")
    _require_text(profile.description, "Search Profile description")
    if not profile.target_roles:
        raise ProfileValidationError("Search Profile requires at least one target role.")

    for label, values in (
        ("target roles", profile.target_roles),
        ("seniority targets", profile.seniority_targets),
        ("preferred technologies", profile.preferred_technologies),
        ("acceptable technologies", profile.acceptable_technologies),
        ("avoided technologies", profile.avoided_technologies),
        ("target locations", profile.target_locations),
        ("employment types", profile.employment_types),
        ("preferred industries", profile.preferred_industries),
        ("avoided industries", profile.avoided_industries),
        ("preferred company characteristics", profile.preferred_company_characteristics),
        ("avoided company characteristics", profile.avoided_company_characteristics),
        ("must haves", profile.must_haves),
        ("must not haves", profile.must_not_haves),
    ):
        _require_unique_nonempty(values, f"Search Profile {label}")

    if len(profile.work_models) != len(set(profile.work_models)):
        raise ProfileValidationError("Search Profile work models must be unique.")
    if any(model not in {"remote", "hybrid", "on_site"} for model in profile.work_models):
        raise ProfileValidationError("Search Profile contains an unsupported work model.")

    technology_sets = [
        {value.casefold() for value in profile.preferred_technologies},
        {value.casefold() for value in profile.acceptable_technologies},
        {value.casefold() for value in profile.avoided_technologies},
    ]
    if technology_sets[0] & technology_sets[1] or technology_sets[0] & technology_sets[2] or technology_sets[1] & technology_sets[2]:
        raise ProfileValidationError("A technology may belong to only one preference tier.")

    if profile.salary_floor is not None and profile.salary_floor < 0:
        raise ProfileValidationError("Salary floor must not be negative.")
    if profile.salary_target is not None and profile.salary_target < 0:
        raise ProfileValidationError("Salary target must not be negative.")
    if profile.salary_floor is not None and profile.salary_target is not None and profile.salary_floor > profile.salary_target:
        raise ProfileValidationError("Salary floor must not exceed salary target.")
    if len(profile.salary_currency.strip()) != 3:
        raise ProfileValidationError("Salary currency must be a three-letter code.")
    if not 1 <= profile.result_limit <= 50:
        raise ProfileValidationError("Search Profile result limit must be between 1 and 50.")
