from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from vocation.domain.criteria import AssessmentCriterion
from vocation.domain.profiles import CriterionPolicy, SearchProfile

ContributionStatus = Literal["scored", "missing", "unscorable"]
HardConstraintStatus = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class AssessmentEvidence:
    criterion_id: str
    value: Any
    origin: str
    reasoning: str | None = None


@dataclass(frozen=True)
class CriterionContribution:
    criterion_id: str
    criterion_name: str
    weight: float
    required: bool
    status: ContributionStatus
    value: Any | None
    origin: str | None
    score: float | None
    weighted_points: float | None
    explanation: str


@dataclass(frozen=True)
class OpportunityFit:
    opportunity_id: str
    search_profile_id: str
    search_profile_revision: int
    candidate_profile_revision: int | None
    hard_constraint_status: HardConstraintStatus
    weighted_fit_score: float | None
    evidence_completeness: float
    contributions: tuple[CriterionContribution, ...]
    hard_failures: tuple[str, ...]
    hard_unknowns: tuple[str, ...]
    missing_evidence: tuple[str, ...]


def _clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def _numeric_score(value: Any, criterion: AssessmentCriterion, policy: CriterionPolicy) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    if criterion.numeric_min is None or criterion.numeric_max is None:
        return None
    span = criterion.numeric_max - criterion.numeric_min
    if span <= 0:
        return None
    normalized = (float(value) - criterion.numeric_min) / span
    if policy.numeric_direction == "lower_is_better":
        normalized = 1.0 - normalized
    return _clamp_percent(normalized * 100.0)


def _categorical_score(value: Any, policy: CriterionPolicy) -> float | None:
    if not isinstance(value, str):
        return None
    scores = {item.value: item.score for item in policy.category_scores}
    return scores.get(value)


def _boolean_score(value: Any, policy: CriterionPolicy) -> float | None:
    if not isinstance(value, bool) or policy.preferred_boolean is None:
        return None
    return 100.0 if value is policy.preferred_boolean else 0.0


def _score(value: Any, criterion: AssessmentCriterion, policy: CriterionPolicy) -> float | None:
    if criterion.value_type == "numeric":
        return _numeric_score(value, criterion, policy)
    if criterion.value_type == "categorical":
        return _categorical_score(value, policy)
    if criterion.value_type == "boolean":
        return _boolean_score(value, policy)
    return None


def _required_failure(value: Any, score: float | None, criterion: AssessmentCriterion, policy: CriterionPolicy) -> str | None:
    if not policy.required:
        return None
    if criterion.value_type == "numeric" and policy.minimum_numeric_value is not None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"{criterion.display_name}: required numeric value is not evaluable"
        if float(value) < policy.minimum_numeric_value:
            return f"{criterion.display_name}: {value} is below required minimum {policy.minimum_numeric_value:g}"
    if policy.minimum_score is not None and score is not None and score < policy.minimum_score:
        return f"{criterion.display_name}: fit {score:.0f}% is below required minimum {policy.minimum_score:.0f}%"
    return None


def evaluate_opportunity_fit(
    *,
    opportunity_id: str,
    search_profile: SearchProfile,
    candidate_profile_revision: int | None,
    criteria: dict[str, AssessmentCriterion],
    assessments: dict[str, AssessmentEvidence],
) -> OpportunityFit:
    contributions: list[CriterionContribution] = []
    hard_failures: list[str] = []
    hard_unknowns: list[str] = []
    missing_evidence: list[str] = []
    total_weight = sum(policy.weight for policy in search_profile.criterion_policies if policy.weight > 0)
    scored_weight = 0.0
    weighted_points = 0.0

    for policy in search_profile.criterion_policies:
        criterion = criteria.get(policy.criterion_id)
        if criterion is None:
            explanation = f"Criterion '{policy.criterion_id}' is not available."
            contributions.append(
                CriterionContribution(
                    criterion_id=policy.criterion_id,
                    criterion_name=policy.criterion_id,
                    weight=policy.weight,
                    required=policy.required,
                    status="unscorable",
                    value=None,
                    origin=None,
                    score=None,
                    weighted_points=None,
                    explanation=explanation,
                )
            )
            missing_evidence.append(explanation)
            if policy.required:
                hard_unknowns.append(explanation)
            continue

        evidence = assessments.get(policy.criterion_id)
        if evidence is None:
            explanation = f"{criterion.display_name}: no assessment evidence available."
            contributions.append(
                CriterionContribution(
                    criterion_id=policy.criterion_id,
                    criterion_name=criterion.display_name,
                    weight=policy.weight,
                    required=policy.required,
                    status="missing",
                    value=None,
                    origin=None,
                    score=None,
                    weighted_points=None,
                    explanation=explanation,
                )
            )
            missing_evidence.append(explanation)
            if policy.required:
                hard_unknowns.append(explanation)
            continue

        score = _score(evidence.value, criterion, policy)
        if score is None:
            explanation = f"{criterion.display_name}: value is present but the Search Profile has no usable scoring rule for it."
            contributions.append(
                CriterionContribution(
                    criterion_id=policy.criterion_id,
                    criterion_name=criterion.display_name,
                    weight=policy.weight,
                    required=policy.required,
                    status="unscorable",
                    value=evidence.value,
                    origin=evidence.origin,
                    score=None,
                    weighted_points=None,
                    explanation=explanation,
                )
            )
            missing_evidence.append(explanation)
            if policy.required:
                hard_unknowns.append(explanation)
            continue

        points = score * policy.weight
        if policy.weight > 0:
            scored_weight += policy.weight
            weighted_points += points
        failure = _required_failure(evidence.value, score, criterion, policy)
        if failure is not None:
            hard_failures.append(failure)
        explanation = f"{criterion.display_name}: {score:.0f}% from {evidence.origin} evidence at weight {policy.weight:g}."
        contributions.append(
            CriterionContribution(
                criterion_id=policy.criterion_id,
                criterion_name=criterion.display_name,
                weight=policy.weight,
                required=policy.required,
                status="scored",
                value=evidence.value,
                origin=evidence.origin,
                score=round(score, 2),
                weighted_points=round(points, 2),
                explanation=explanation,
            )
        )

    for item in search_profile.must_haves:
        hard_unknowns.append(f"Must-have not yet structurally verified: {item}")
    for item in search_profile.must_not_haves:
        hard_unknowns.append(f"Exclusion condition not yet structurally verified: {item}")

    if hard_failures:
        hard_status: HardConstraintStatus = "fail"
    elif hard_unknowns:
        hard_status = "unknown"
    else:
        hard_status = "pass"

    fit_score = round(weighted_points / scored_weight, 2) if scored_weight > 0 else None
    completeness = round((scored_weight / total_weight) * 100.0, 2) if total_weight > 0 else 0.0

    return OpportunityFit(
        opportunity_id=opportunity_id,
        search_profile_id=search_profile.id,
        search_profile_revision=search_profile.revision,
        candidate_profile_revision=candidate_profile_revision,
        hard_constraint_status=hard_status,
        weighted_fit_score=fit_score,
        evidence_completeness=completeness,
        contributions=tuple(contributions),
        hard_failures=tuple(hard_failures),
        hard_unknowns=tuple(hard_unknowns),
        missing_evidence=tuple(missing_evidence),
    )
