from __future__ import annotations

import json
from pathlib import Path

from vocation.domain.criteria import AssessmentCriterion
from vocation.domain.fit import AssessmentEvidence, evaluate_opportunity_fit
from vocation.domain.profiles import CategoryScore, CriterionPolicy, SearchProfile

ROOT = Path(__file__).resolve().parents[2]


def valid_bundle() -> dict:
    return json.loads((ROOT / "examples" / "imports" / "initial-valid.json").read_text(encoding="utf-8"))


def search_payload(*, include_missing: bool = False, constraints: bool = False) -> dict:
    policies = [
        {
            "criterion_id": "junior_suitability",
            "weight": 2,
            "required": True,
            "numeric_direction": "higher_is_better",
            "minimum_numeric_value": 4,
            "minimum_score": 70,
            "preferred_boolean": None,
            "category_scores": [],
        }
    ]
    if include_missing:
        policies.append(
            {
                "criterion_id": "technology_fit",
                "weight": 3,
                "required": False,
                "numeric_direction": "higher_is_better",
                "minimum_numeric_value": None,
                "minimum_score": None,
                "preferred_boolean": None,
                "category_scores": [],
            }
        )
    return {
        "name": "Qualitative Suche",
        "description": "Wenige hochwertige Einstiegsstellen",
        "target_roles": ["Junior Softwareentwickler"],
        "seniority_targets": ["junior"],
        "preferred_technologies": ["Java"],
        "acceptable_technologies": [],
        "avoided_technologies": [],
        "target_locations": ["Hamburg"],
        "work_models": ["hybrid"],
        "relocation_willing": False,
        "employment_types": ["full-time"],
        "preferred_industries": [],
        "avoided_industries": [],
        "preferred_company_characteristics": [],
        "avoided_company_characteristics": [],
        "salary_floor": None,
        "salary_target": None,
        "salary_currency": "EUR",
        "must_haves": ["Berufseinstieg möglich"] if constraints else [],
        "must_not_haves": ["Senior-only"] if constraints else [],
        "result_limit": 10,
        "criterion_policies": policies,
    }


def seed_market_and_profile(client, *, include_missing: bool = False, constraints: bool = False) -> tuple[str, str]:
    imported = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle(), ensure_ascii=False)})
    assert imported.status_code == 200
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    profile = client.post("/api/profiles/search", json=search_payload(include_missing=include_missing, constraints=constraints))
    assert profile.status_code == 201
    profile_id = profile.json()["id"]
    assert client.post(f"/api/profiles/search/{profile_id}/default").status_code == 200
    return opportunity_id, profile_id


def test_fit_uses_external_assessment_and_keeps_fit_separate_from_completeness(client) -> None:
    opportunity_id, profile_id = seed_market_and_profile(client, include_missing=True)
    candidate = client.put(
        "/api/profiles/candidate",
        json={"headline": "Softwareentwickler", "summary": "Privates Kandidatenprofil"},
    )
    assert candidate.status_code == 200

    response = client.get("/api/opportunity-fit")
    assert response.status_code == 200
    fit = response.json()[0]
    assert fit["opportunity_id"] == opportunity_id
    assert fit["search_profile_id"] == profile_id
    assert fit["search_profile_revision"] == 1
    assert fit["candidate_profile_revision"] is None
    assert fit["hard_constraint_status"] == "pass"
    assert fit["weighted_fit_score"] == 100
    assert fit["evidence_completeness"] == 40
    assert fit["contributions"][0]["origin"] == "external_research"
    assert fit["contributions"][0]["score"] == 100
    assert fit["contributions"][1]["status"] == "missing"
    assert any("Technologie-Passung" in item for item in fit["missing_evidence"])


def test_personal_assessment_takes_precedence_and_required_threshold_can_fail(client) -> None:
    opportunity_id, _ = seed_market_and_profile(client)
    before = client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"]

    assessment = client.post(
        f"/api/opportunities/{opportunity_id}/assessments/personal",
        json={"criterion_id": "junior_suitability", "value": 3, "reasoning": "Persönlich zu anspruchsvoll eingeschätzt."},
    )
    assert assessment.status_code == 201

    response = client.get(f"/api/opportunities/{opportunity_id}/fit")
    assert response.status_code == 200
    fit = response.json()
    assert fit["weighted_fit_score"] == 50
    assert fit["evidence_completeness"] == 100
    assert fit["hard_constraint_status"] == "fail"
    assert fit["contributions"][0]["origin"] == "personal"
    assert any("below required minimum 4" in item for item in fit["hard_failures"])
    assert client.get(f"/api/opportunities/{opportunity_id}").json()["tracking_status"] == before


def test_free_text_search_constraints_remain_explicitly_unknown_until_structured_research_exists(client) -> None:
    opportunity_id, _ = seed_market_and_profile(client, constraints=True)
    fit = client.get(f"/api/opportunities/{opportunity_id}/fit").json()

    assert fit["weighted_fit_score"] == 100
    assert fit["hard_constraint_status"] == "unknown"
    assert any("Must-have not yet structurally verified" in item for item in fit["hard_unknowns"])
    assert any("Exclusion condition not yet structurally verified" in item for item in fit["hard_unknowns"])


def test_fit_requires_an_explicit_or_default_search_profile(client) -> None:
    imported = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle(), ensure_ascii=False)})
    assert imported.status_code == 200
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]

    response = client.get(f"/api/opportunities/{opportunity_id}/fit")
    assert response.status_code == 409
    assert "No default Search Profile" in response.json()["detail"]


def test_categorical_policy_is_explicit_and_not_inferred_from_allowed_value_order() -> None:
    criterion = AssessmentCriterion(
        criterion_id="work_model_fit",
        display_name="Arbeitsmodell-Passung",
        description="Arbeitsmodell",
        value_type="categorical",
        applicable_subject_type="opportunity",
        active=True,
        display_order=1,
        allowed_values=("good", "acceptable", "poor", "unknown"),
    )
    profile = SearchProfile(
        id="search",
        revision=1,
        name="Search",
        description="Search",
        target_roles=("Developer",),
        criterion_policies=(
            CriterionPolicy(
                criterion_id="work_model_fit",
                weight=4,
                category_scores=(
                    CategoryScore("good", 100),
                    CategoryScore("acceptable", 65),
                    CategoryScore("poor", 10),
                ),
            ),
        ),
    )

    fit = evaluate_opportunity_fit(
        opportunity_id="opportunity",
        search_profile=profile,
        candidate_profile_revision=None,
        criteria={criterion.criterion_id: criterion},
        assessments={
            criterion.criterion_id: AssessmentEvidence(
                criterion_id=criterion.criterion_id,
                value="acceptable",
                origin="external_research",
            )
        },
    )

    assert fit.weighted_fit_score == 65
    assert fit.evidence_completeness == 100
    assert fit.contributions[0].score == 65


def test_zero_weight_policy_is_disabled_for_fit_and_completeness() -> None:
    enabled = AssessmentCriterion(
        criterion_id="enabled",
        display_name="Enabled",
        description="Enabled",
        value_type="numeric",
        applicable_subject_type="opportunity",
        active=True,
        display_order=1,
        numeric_min=0,
        numeric_max=10,
    )
    disabled = AssessmentCriterion(
        criterion_id="disabled",
        display_name="Disabled",
        description="Disabled",
        value_type="numeric",
        applicable_subject_type="opportunity",
        active=True,
        display_order=2,
        numeric_min=0,
        numeric_max=10,
    )
    profile = SearchProfile(
        id="search",
        revision=1,
        name="Search",
        description="Search",
        target_roles=("Developer",),
        criterion_policies=(
            CriterionPolicy(criterion_id="enabled", weight=2),
            CriterionPolicy(criterion_id="disabled", weight=0),
        ),
    )

    fit = evaluate_opportunity_fit(
        opportunity_id="opportunity",
        search_profile=profile,
        candidate_profile_revision=None,
        criteria={enabled.criterion_id: enabled, disabled.criterion_id: disabled},
        assessments={
            enabled.criterion_id: AssessmentEvidence(
                criterion_id=enabled.criterion_id,
                value=8,
                origin="external_research",
            )
        },
    )

    assert fit.weighted_fit_score == 80
    assert fit.evidence_completeness == 100
    assert fit.contributions[1].status == "missing"
