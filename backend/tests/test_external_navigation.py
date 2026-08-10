from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from vocation.application.external_navigation import (
    BrowserOpenError,
    ExternalLinkNotFoundError,
    ExternalNavigationService,
    OpportunityNotFoundError,
)
from vocation.domain.external_links import ExternalLink, ExternalLinkPolicy, ExternalLinkPolicyError, PreferredPostingSelector

NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


def link(
    posting_id: str = "posting-1",
    *,
    url: str = "https://example.com/job",
    source_type: str = "other",
    availability: str = "unknown",
    observed_at: datetime = NOW,
) -> ExternalLink:
    return ExternalLink(
        posting_id,
        "source-1",
        "Example",
        source_type,  # type: ignore[arg-type]
        url,
        "Example job",
        availability,  # type: ignore[arg-type]
        observed_at,
    )


@pytest.mark.parametrize("url", ["https://example.com/job", "https://example.com"])
def test_external_link_policy_accepts_absolute_https_with_host(url: str) -> None:
    assert ExternalLinkPolicy().validate(link(url=url)).url == url


@pytest.mark.parametrize("url", ["http://example.com", "/relative", "https:///missing-host", "javascript:alert(1)", "https://"])
def test_external_link_policy_rejects_non_https_or_hostless_urls(url: str) -> None:
    with pytest.raises(ExternalLinkPolicyError) as error:
        ExternalLinkPolicy().validate(link(url=url))
    assert error.value.code == "INVALID_EXTERNAL_LINK"


def test_selector_uses_exact_precedence_without_mutating_inputs() -> None:
    candidates = [
        link("unavailable", availability="unavailable", source_type="company_careers"),
        link("unknown", availability="unknown", source_type="other"),
        link("available-board", availability="available", source_type="job_board"),
        link("available-careers", availability="available", source_type="company_careers"),
    ]
    selected = PreferredPostingSelector().select(candidates)
    assert [item.posting_id for item in selected if item.preferred] == ["available-careers"]
    assert all(not item.preferred for item in candidates)


def test_selector_uses_newest_then_lexical_posting_id_tiebreak() -> None:
    candidates = [
        link("z", source_type="company_careers", observed_at=NOW - timedelta(days=1)),
        link("b", source_type="company_careers", observed_at=NOW),
        link("a", source_type="company_careers", observed_at=NOW),
    ]
    selected = PreferredPostingSelector().select(candidates)
    assert [item.posting_id for item in selected if item.preferred] == ["a"]
    assert PreferredPostingSelector().select([]) == ()


class FakeLinks:
    def __init__(self, candidates: dict[str, list[ExternalLink] | None]):
        self.candidates = candidates

    def links_for_opportunity(self, opportunity_id: str) -> list[ExternalLink] | None:
        return self.candidates.get(opportunity_id)

    def links_for_posting(self, opportunity_id: str, posting_id: str) -> list[ExternalLink] | None:
        candidates = self.candidates.get(opportunity_id)
        if candidates is None:
            return None
        return [item for item in candidates if item.posting_id == posting_id]


class FakeBrowser:
    def __init__(self) -> None:
        self.urls: list[str] = []

    def open(self, url: str) -> None:
        self.urls.append(url)


def test_navigation_lists_valid_links_and_explicit_posting_override() -> None:
    browser = FakeBrowser()
    repository = FakeLinks({"opportunity-1": [link("a", url="http://bad.example"), link("b", url="https://good.example/job")]})
    service = ExternalNavigationService(repository, browser)
    listed = service.links_for_opportunity("opportunity-1")
    assert [item.posting_id for item in listed] == ["b"]
    opened = service.open_opportunity("opportunity-1", "b")
    assert opened.posting_id == "b"
    assert browser.urls == ["https://good.example/job"]


def test_invalid_explicit_posting_never_falls_back() -> None:
    browser = FakeBrowser()
    repository = FakeLinks({"opportunity-1": [link("a", url="https://a.example/job"), link("b", url="https://b.example/job")]})
    service = ExternalNavigationService(repository, browser)
    with pytest.raises(ExternalLinkNotFoundError):
        service.open_opportunity("opportunity-1", "missing")
    assert browser.urls == []


def test_navigation_no_link_unknown_opportunity_and_browser_called_once() -> None:
    browser = FakeBrowser()
    service = ExternalNavigationService(FakeLinks({"opportunity-1": [link(url="http://bad.example")]}), browser)
    with pytest.raises(ExternalLinkNotFoundError):
        service.open_opportunity("opportunity-1")
    with pytest.raises(OpportunityNotFoundError):
        service.links_for_opportunity("missing")
    assert browser.urls == []


class FailingBrowser:
    def open(self, url: str) -> None:
        assert url.startswith("https://")
        raise BrowserOpenError("Browser could not open URL.")


def test_browser_failure_is_deterministic_after_final_url_guard() -> None:
    service = ExternalNavigationService(FakeLinks({"opportunity-1": [link()]}), FailingBrowser())
    with pytest.raises(BrowserOpenError):
        service.open_opportunity("opportunity-1")
