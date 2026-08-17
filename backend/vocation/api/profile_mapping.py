from __future__ import annotations

from vocation.api.profile_schemas import (
    CandidateProfilePayload,
    CandidateProfileResponse,
    EducationPayload,
    LanguagePayload,
    ProjectHighlightPayload,
    SearchProfilePayload,
    SearchProfileResponse,
    SkillPayload,
)
from vocation.domain.profiles import CandidateProfile, Education, Language, ProjectHighlight, SearchProfile, Skill


def candidate_from_payload(payload: CandidateProfilePayload) -> CandidateProfile:
    return CandidateProfile(
        revision=1,
        headline=payload.headline,
        summary=payload.summary,
        education=tuple(Education(**item.model_dump()) for item in payload.education),
        skills=tuple(Skill(**item.model_dump()) for item in payload.skills),
        languages=tuple(Language(**item.model_dump()) for item in payload.languages),
        experience_summary=payload.experience_summary,
        projects=tuple(
            ProjectHighlight(name=item.name, summary=item.summary, technologies=tuple(item.technologies)) for item in payload.projects
        ),
        interests=tuple(payload.interests),
    )


def search_from_payload(payload: SearchProfilePayload) -> SearchProfile:
    return SearchProfile(
        id="pending",
        revision=1,
        name=payload.name,
        description=payload.description,
        target_roles=tuple(payload.target_roles),
        seniority_targets=tuple(payload.seniority_targets),
        preferred_technologies=tuple(payload.preferred_technologies),
        acceptable_technologies=tuple(payload.acceptable_technologies),
        avoided_technologies=tuple(payload.avoided_technologies),
        target_locations=tuple(payload.target_locations),
        work_models=tuple(payload.work_models),
        relocation_willing=payload.relocation_willing,
        employment_types=tuple(payload.employment_types),
        preferred_industries=tuple(payload.preferred_industries),
        avoided_industries=tuple(payload.avoided_industries),
        preferred_company_characteristics=tuple(payload.preferred_company_characteristics),
        avoided_company_characteristics=tuple(payload.avoided_company_characteristics),
        salary_floor=payload.salary_floor,
        salary_target=payload.salary_target,
        salary_currency=payload.salary_currency.upper(),
        must_haves=tuple(payload.must_haves),
        must_not_haves=tuple(payload.must_not_haves),
        result_limit=payload.result_limit,
    )


def candidate_response(profile: CandidateProfile) -> CandidateProfileResponse:
    return CandidateProfileResponse(
        revision=profile.revision,
        headline=profile.headline,
        summary=profile.summary,
        education=[EducationPayload(**item.__dict__) for item in profile.education],
        skills=[SkillPayload(**item.__dict__) for item in profile.skills],
        languages=[LanguagePayload(**item.__dict__) for item in profile.languages],
        experience_summary=profile.experience_summary,
        projects=[ProjectHighlightPayload(name=item.name, summary=item.summary, technologies=list(item.technologies)) for item in profile.projects],
        interests=list(profile.interests),
    )


def search_response(profile: SearchProfile) -> SearchProfileResponse:
    return SearchProfileResponse(
        id=profile.id,
        revision=profile.revision,
        is_default=profile.is_default,
        name=profile.name,
        description=profile.description,
        target_roles=list(profile.target_roles),
        seniority_targets=list(profile.seniority_targets),
        preferred_technologies=list(profile.preferred_technologies),
        acceptable_technologies=list(profile.acceptable_technologies),
        avoided_technologies=list(profile.avoided_technologies),
        target_locations=list(profile.target_locations),
        work_models=list(profile.work_models),
        relocation_willing=profile.relocation_willing,
        employment_types=list(profile.employment_types),
        preferred_industries=list(profile.preferred_industries),
        avoided_industries=list(profile.avoided_industries),
        preferred_company_characteristics=list(profile.preferred_company_characteristics),
        avoided_company_characteristics=list(profile.avoided_company_characteristics),
        salary_floor=profile.salary_floor,
        salary_target=profile.salary_target,
        salary_currency=profile.salary_currency,
        must_haves=list(profile.must_haves),
        must_not_haves=list(profile.must_not_haves),
        result_limit=profile.result_limit,
    )
