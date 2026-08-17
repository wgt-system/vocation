from __future__ import annotations

from typing import Protocol

from vocation.application.ports import ExternalLinkRepository
from vocation.domain.external_links import ExternalLink, ExternalLinkPolicy, PreferredPostingSelector


class BrowserOpenError(RuntimeError):
    code = "BROWSER_OPEN_FAILED"


class OpportunityNotFoundError(LookupError):
    code = "OPPORTUNITY_NOT_FOUND"


class ExternalLinkNotFoundError(LookupError):
    code = "NO_EXTERNAL_LINK"


class BrowserAdapter(Protocol):
    def open(self, url: str) -> None: ...


class ExternalNavigationService:
    def __init__(
        self,
        repository: ExternalLinkRepository,
        browser: BrowserAdapter,
        policy: ExternalLinkPolicy | None = None,
        selector: PreferredPostingSelector | None = None,
    ):
        self.repository = repository
        self.browser = browser
        self.policy = policy or ExternalLinkPolicy()
        self.selector = selector or PreferredPostingSelector()

    def links_for_opportunity(self, opportunity_id: str) -> tuple[ExternalLink, ...]:
        candidates = self.repository.links_for_opportunity(opportunity_id)
        if candidates is None:
            raise OpportunityNotFoundError(f"Opportunity '{opportunity_id}' does not exist.")
        return self.selector.select(self.policy.filter_valid(candidates))

    def open_opportunity(self, opportunity_id: str, posting_id: str | None = None) -> ExternalLink:
        if posting_id is None:
            candidates = self.repository.links_for_opportunity(opportunity_id)
            if candidates is None:
                raise OpportunityNotFoundError(f"Opportunity '{opportunity_id}' does not exist.")
            valid = self.policy.filter_valid(candidates)
            selected = next((link for link in self.selector.select(valid) if link.preferred), None)
        else:
            candidates = self.repository.links_for_posting(opportunity_id, posting_id)
            if candidates is None:
                raise OpportunityNotFoundError(f"Opportunity '{opportunity_id}' or Posting '{posting_id}' does not exist.")
            valid = self.policy.filter_valid(candidates)
            selected = next((link for link in self.selector.select(valid) if link.posting_id == posting_id), None)
        if selected is None:
            raise ExternalLinkNotFoundError("No valid external link is available for the requested Posting.")
        self.policy.validate(selected)
        self.browser.open(selected.url)
        return selected
