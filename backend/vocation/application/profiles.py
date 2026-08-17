from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Protocol
from uuid import uuid4

from vocation.domain.criteria import AssessmentCriterion
from vocation.domain.profiles import (
    CandidateProfile,
    ProfileValidationError,
    SearchProfile,
    validate_candidate_profile,
    validate_criterion_policy_against_criterion,
    validate_search_profile,
)


class ProfileRepository(Protocol):
    def get_candidate_profile(self) -> CandidateProfile | None: ...

    def save_candidate_profile(self, profile: CandidateProfile) -> CandidateProfile: ...

    def list_search_profiles(self) -> list[SearchProfile]: ...

    def get_search_profile(self, profile_id: str) -> SearchProfile | None: ...

    def get_default_search_profile(self) -> SearchProfile | None: ...

    def create_search_profile(self, profile: SearchProfile) -> SearchProfile: ...

    def revise_search_profile(self, profile_id: str, profile: SearchProfile) -> SearchProfile: ...

    def set_default_search_profile(self, profile_id: str) -> SearchProfile: ...

    def delete_search_profile(self, profile_id: str) -> None: ...


class CriterionReader(Protocol):
    def get(self, criterion_id: str) -> AssessmentCriterion | None: ...


class ProfileService:
    def __init__(
        self,
        repository: ProfileRepository,
        id_factory: Callable[[], str] = lambda: str(uuid4()),
        *,
        criteria: CriterionReader | None = None,
    ):
        self.repository = repository
        self.id_factory = id_factory
        self.criteria = criteria

    def get_candidate_profile(self) -> CandidateProfile | None:
        return self.repository.get_candidate_profile()

    def save_candidate_profile(self, profile: CandidateProfile) -> CandidateProfile:
        candidate = replace(profile, revision=max(profile.revision, 1))
        validate_candidate_profile(candidate)
        return self.repository.save_candidate_profile(candidate)

    def list_search_profiles(self) -> list[SearchProfile]:
        return self.repository.list_search_profiles()

    def get_search_profile(self, profile_id: str) -> SearchProfile | None:
        return self.repository.get_search_profile(profile_id)

    def get_default_search_profile(self) -> SearchProfile | None:
        return self.repository.get_default_search_profile()

    def create_search_profile(self, profile: SearchProfile) -> SearchProfile:
        created = replace(profile, id=self.id_factory(), revision=1)
        self._validate_search_profile(created)
        return self.repository.create_search_profile(created)

    def revise_search_profile(self, profile_id: str, profile: SearchProfile) -> SearchProfile:
        revised = replace(profile, id=profile_id, revision=max(profile.revision, 1))
        self._validate_search_profile(revised)
        return self.repository.revise_search_profile(profile_id, revised)

    def set_default_search_profile(self, profile_id: str) -> SearchProfile:
        return self.repository.set_default_search_profile(profile_id)

    def delete_search_profile(self, profile_id: str) -> None:
        self.repository.delete_search_profile(profile_id)

    def _validate_search_profile(self, profile: SearchProfile) -> None:
        validate_search_profile(profile)
        if self.criteria is None:
            return
        for policy in profile.criterion_policies:
            criterion = self.criteria.get(policy.criterion_id)
            if criterion is None:
                raise ProfileValidationError(f"Criterion policy references unknown criterion '{policy.criterion_id}'.")
            validate_criterion_policy_against_criterion(policy, criterion)
