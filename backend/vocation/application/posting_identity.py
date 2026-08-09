from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vocation.application.ports import PostingIdentityRepository
from vocation.domain.research_bundle import (
    PostingIdentity,
    PostingIdentityConflictError,
    PostingIdentityInput,
)

ResolutionKind = Literal["external_posting_id", "url", "correlation", "unresolved"]


@dataclass(frozen=True)
class PostingIdentityResolution:
    posting: PostingIdentity | None
    kind: ResolutionKind

    @property
    def resolved(self) -> bool:
        return self.posting is not None


class PostingIdentityResolver:
    def __init__(self, repository: PostingIdentityRepository):
        self.repository = repository

    def resolve(self, identity: PostingIdentityInput) -> PostingIdentityResolution:
        url_match = self.repository.find_by_normalized_canonical_url(identity.normalized_source_reference_url)
        stable_match = self.repository.find_by_stable_key(identity.stable_key) if identity.stable_key else None
        correlated = self.repository.get_posting(identity.correlated_posting_id) if identity.correlated_posting_id else None
        if identity.correlated_posting_id and correlated is None:
            raise PostingIdentityConflictError("The correlated Posting does not exist.")

        if stable_match and url_match and stable_match.posting_id != url_match.posting_id:
            raise PostingIdentityConflictError("Stable key and canonical URL resolve to different Postings.")

        if identity.stable_key:
            if stable_match:
                if correlated and stable_match.posting_id != correlated.posting_id:
                    raise PostingIdentityConflictError("Correlation and deterministic identity resolve to different Postings.")
                return PostingIdentityResolution(stable_match, "external_posting_id")
            if url_match:
                if correlated and url_match.posting_id == correlated.posting_id:
                    return PostingIdentityResolution(correlated, "correlation")
                raise PostingIdentityConflictError("The canonical URL belongs to another Posting.")
        elif url_match:
            if correlated and url_match.posting_id != correlated.posting_id:
                raise PostingIdentityConflictError("Correlation and deterministic identity resolve to different Postings.")
            return PostingIdentityResolution(url_match, "url")

        if correlated:
            return PostingIdentityResolution(correlated, "correlation")

        return PostingIdentityResolution(None, "unresolved")
