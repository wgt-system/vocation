from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vocation.domain.criteria import AssessmentCriterion

SkillLevel = Literal["learning", "basic", "working", "strong", "expert"]
WorkModel = Literal["remote", "hybrid", "on_site"]
NumericDirection = Literal["higher_is_better", "lower_is_better"]


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
class CategoryScore:
    value: str
    score: float


@dataclass(frozen=True)
class CriterionPolicy:
    criterion_id: str
    weight: float = 1.0
    required: bool = False
    numeric_direction: NumericDirection = "higher_is_better"
    minimum_numeric_value: float | None = None
    minimum_score: float | None = None
    preferred_boolean: bool | None = None
    category_scores: tuple[CategoryScore, ...] = ()


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
    criterion_policies: tuple[CriterionPolicy, ...] = ()
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


def validate_criterion_policy(policy: CriterionPolicy) -> None:
    _require_text(policy.criterion_id, "Criterion policy criterion ID")
    if not 0 <= policy.weight <= 10:
        raise ProfileValidationError("Criterion policy weight must be between 0 and 10.")
    if policy.numeric_direction not in {"higher_is_better", "lower_is_better"}:
        raise ProfileValidationError("Criterion policy numeric direction is invalid.")
    if policy.minimum_score is not None and not 0 <= policy.minimum_score <= 100:
        raise ProfileValidationError("Criterion policy minimum score must be between 0 and 100.")
    category_values = [item.value.strip().casefold() for item in policy.category_scores]
    if any(not value for value in category_values):
        raise ProfileValidationError("Criterion category score values must be non-empty.")
    if len(category_values) != len(set(category_values)):
        raise ProfileValidationError("Criterion category score values must be unique.")
    if any(not 0 <= item.score <= 100 for item in policy.category_scores):
        raise ProfileValidationError("Criterion category scores must be between 0 and 100.")


def validate_criterion_policy_against_criterion(
    policy: CriterionPolicy,
    criterion: AssessmentCriterion,
) -> None:
    if policy.criterion_id != criterion.criterion_id:
        raise ProfileValidationError("Criterion policy does not match its referenced criterion.")
    if criterion.applicable_subject_type != "opportunity":
        raise ProfileValidationError(
            f"Criterion policy '{policy.criterion_id}' must reference an opportunity criterion."
        )

    if criterion.value_type == "text":
        if (
            policy.weight > 0
            or policy.required
            or policy.minimum_numeric_value is not None
            or policy.minimum_score is not None
            or policy.preferred_boolean is not None
            or policy.category_scores
        ):
            raise ProfileValidationError(
                f"Text criterion '{policy.criterion_id}' cannot define automatic fit or hard-threshold policy."
            )
        return

    if criterion.value_type != "numeric" and policy.minimum_numeric_value is not None:
        raise ProfileValidationError(
            f"Only numeric criterion '{policy.criterion_id}' may define a minimum numeric value."
        )
    if criterion.value_type != "boolean" and policy.preferred_boolean is not None:
        raise ProfileValidationError(
            f"Only boolean criterion '{policy.criterion_id}' may define a preferred boolean value."
        )
    if criterion.value_type != "categorical" and policy.category_scores:
        raise ProfileValidationError(
            f"Only categorical criterion '{policy.criterion_id}' may define category scores."
        )

    if criterion.value_type == "numeric":
        if policy.minimum_numeric_value is not None and not (
            criterion.numeric_min <= policy.minimum_numeric_value <= criterion.numeric_max
        ):
            raise ProfileValidationError(
                f"Minimum numeric value for criterion '{policy.criterion_id}' must stay within the criterion range."
            )
        if policy.required and policy.minimum_numeric_value is None and policy.minimum_score is None:
            raise ProfileValidationError(
                f"Required numeric criterion '{policy.criterion_id}' needs a deterministic minimum value or score."
            )
        return

    if criterion.value_type == "boolean":
        if (policy.weight > 0 or policy.minimum_score is not None or policy.required) and policy.preferred_boolean is None:
            raise ProfileValidationError(
                f"Boolean criterion '{policy.criterion_id}' needs a preferred value before it can be scored."
            )
        if policy.required and policy.minimum_score is None:
            raise ProfileValidationError(
                f"Required boolean criterion '{policy.criterion_id}' needs a minimum score."
            )
        return

    configured_values = {item.value for item in policy.category_scores}
    allowed_values = set(criterion.allowed_values)
    if configured_values - allowed_values:
        raise ProfileValidationError(
            f"Categorical criterion '{policy.criterion_id}' contains scores for unsupported values."
        )
    if policy.weight > 0 or policy.minimum_score is not None or policy.required:
        if configured_values != allowed_values:
            raise ProfileValidationError(
                f"Categorical criterion '{policy.criterion_id}' needs an explicit score for every allowed value."
            )
    if policy.required and policy.minimum_score is None:
        raise ProfileValidationError(
            f"Required categorical criterion '{policy.criterion_id}' needs a minimum score."
        )


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

    criterion_ids = [policy.criterion_id for policy in profile.criterion_policies]
    if len(criterion_ids) != len(set(criterion_ids)):
        raise ProfileValidationError("Search Profile criterion policies must use unique criterion IDs.")
    for policy in profile.criterion_policies:
        validate_criterion_policy(policy)
