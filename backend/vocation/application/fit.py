from __future__ import annotations

from typing import Protocol

from vocation.application.criteria import CriteriaService
from vocation.application.profiles import ProfileRepository
from vocation.domain.fit import AssessmentEvidence, OpportunityFit, evaluate_opportunity_fit
from vocation.domain.profiles import SearchProfile


class FitRepository(Protocol):
    def opportunity_exists(self, opportunity_id: str) -> bool: ...

    def opportunity_ids(self) -> list[str]: ...

    def effective_assessments(self, opportunity_id: str) -> dict[str, AssessmentEvidence]: ...


class OpportunityFitNotFoundError(LookupError):
    pass


class SearchProfileRequiredError(ValueError):
    pass


class OpportunityFitService:
    def __init__(self, repository: FitRepository, profiles: ProfileRepository, criteria: CriteriaService):
        self.repository = repository
        self.profiles = profiles
        self.criteria = criteria

    def get(self, opportunity_id: str, search_profile_id: str | None = None) -> OpportunityFit:
        if not self.repository.opportunity_exists(opportunity_id):
            raise OpportunityFitNotFoundError(opportunity_id)
        profile = self._profile(search_profile_id)
        return self._evaluate(opportunity_id, profile)

    def list(self, search_profile_id: str | None = None, opportunity_ids: list[str] | None = None) -> list[OpportunityFit]:
        profile = self._profile(search_profile_id)
        ids = self.repository.opportunity_ids() if opportunity_ids is None else opportunity_ids
        missing = [opportunity_id for opportunity_id in ids if not self.repository.opportunity_exists(opportunity_id)]
        if missing:
            raise OpportunityFitNotFoundError(missing[0])
        return [self._evaluate(opportunity_id, profile) for opportunity_id in ids]

    def _profile(self, search_profile_id: str | None) -> SearchProfile:
        profile = (
            self.profiles.get_search_profile(search_profile_id)
            if search_profile_id is not None
            else self.profiles.get_default_search_profile()
        )
        if profile is None:
            if search_profile_id is None:
                raise SearchProfileRequiredError("No default Search Profile is configured.")
            raise SearchProfileRequiredError(f"Search Profile '{search_profile_id}' does not exist.")
        return profile

    def _evaluate(self, opportunity_id: str, profile: SearchProfile) -> OpportunityFit:
        candidate = self.profiles.get_candidate_profile()
        criteria = {criterion.criterion_id: criterion for criterion in self.criteria.list()}
        return evaluate_opportunity_fit(
            opportunity_id=opportunity_id,
            search_profile=profile,
            candidate_profile_revision=None if candidate is None else candidate.revision,
            criteria=criteria,
            assessments=self.repository.effective_assessments(opportunity_id),
        )
