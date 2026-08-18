from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from vocation.application.criteria import CriteriaService
from vocation.application.profiles import ProfileRepository
from vocation.domain.profiles import CandidateProfile, SearchProfile


class InitialResearchPromptRepository(Protocol):
    def save(
        self,
        *,
        search_profile: SearchProfile,
        candidate_profile: CandidateProfile | None,
        research_scope: dict,
        as_of_date: str,
        criteria_snapshot: list[dict],
        prompt_text: str,
    ) -> tuple[str, str]: ...


@dataclass(frozen=True)
class GeneratedInitialResearchPrompt:
    prompt_run_id: str
    prompt_context_ref: str
    prompt_text: str
    bundle_version: str
    criteria_count: int


class InitialResearchService:
    def __init__(
        self,
        criteria: CriteriaService,
        profiles: ProfileRepository,
        prompt_runs: InitialResearchPromptRepository,
        template_path: Path,
        output_contract_path: Path,
    ):
        self.criteria = criteria
        self.profiles = profiles
        self.prompt_runs = prompt_runs
        self.template_path = template_path
        self.output_contract_path = output_contract_path

    def generate(
        self,
        *,
        search_profile_selector: str,
        extra_constraints: list[str],
        include_candidate_profile: bool,
        as_of_date: str,
    ) -> GeneratedInitialResearchPrompt:
        profile = self._resolve_search_profile(search_profile_selector)
        candidate = self.profiles.get_candidate_profile() if include_candidate_profile else None
        constraints = self._constraints(profile, extra_constraints)
        research_scope = {
            "type": "initial_market_research",
            "as_of_date": as_of_date,
            "search_profile": profile.name,
            "constraints": constraints,
        }
        active_criteria = self.criteria.active_snapshot()
        template = self.template_path.read_text(encoding="utf-8")
        contract = self.output_contract_path.read_text(encoding="utf-8")
        prompt_text = (
            template.replace("{{SEARCH_PROFILE}}", self._external_search_profile(profile))
            .replace("{{CANDIDATE_PROFILE}}", self._external_candidate_profile(candidate))
            .replace("{{RESEARCH_SCOPE}}", json.dumps(research_scope, ensure_ascii=False, indent=2, sort_keys=True))
            .replace("{{AS_OF_DATE}}", as_of_date)
            .replace(
                "{{ACTIVE_ASSESSMENT_CRITERIA}}",
                json.dumps(active_criteria, ensure_ascii=False, indent=2, sort_keys=True),
            )
            .replace("{{OUTPUT_CONTRACT}}", contract)
        )
        prompt_run_id, prompt_context_ref = self.prompt_runs.save(
            search_profile=profile,
            candidate_profile=candidate,
            research_scope=research_scope,
            as_of_date=as_of_date,
            criteria_snapshot=active_criteria,
            prompt_text=prompt_text,
        )
        return GeneratedInitialResearchPrompt(
            prompt_run_id=prompt_run_id,
            prompt_context_ref=prompt_context_ref,
            prompt_text=prompt_text,
            bundle_version="1.0",
            criteria_count=len(active_criteria),
        )

    def _resolve_search_profile(self, selector: str) -> SearchProfile:
        selector = selector.strip()
        if not selector:
            profile = self.profiles.get_default_search_profile()
            if profile is None:
                raise ValueError("No default Search Profile is configured.")
            return profile

        direct = self.profiles.get_search_profile(selector)
        if direct is not None:
            return direct
        by_name = [profile for profile in self.profiles.list_search_profiles() if profile.name == selector]
        if len(by_name) == 1:
            return by_name[0]
        raise ValueError(f"Search Profile '{selector}' does not exist.")

    @staticmethod
    def _constraints(profile: SearchProfile, extra_constraints: list[str]) -> list[str]:
        result = [f"Must have: {value}" for value in profile.must_haves]
        result.extend(f"Must not have: {value}" for value in profile.must_not_haves)
        result.extend(value.strip() for value in extra_constraints if value.strip())
        return list(dict.fromkeys(result))

    @staticmethod
    def _external_search_profile(profile: SearchProfile) -> str:
        payload = asdict(profile)
        payload.pop("id", None)
        payload.pop("is_default", None)
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)

    @staticmethod
    def _external_candidate_profile(profile: CandidateProfile | None) -> str:
        if profile is None:
            return "Not included in this research run."
        return json.dumps(asdict(profile), ensure_ascii=False, indent=2, sort_keys=True)
