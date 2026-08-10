from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Literal
from urllib.parse import urlsplit

from vocation.domain.availability import DerivedAvailability

SourceType = Literal["company_careers", "job_board", "professional_network", "other"]


@dataclass(frozen=True)
class ExternalLink:
    posting_id: str
    source_id: str
    source_name: str
    source_type: SourceType
    url: str
    display_label: str | None
    availability: DerivedAvailability
    observed_at: datetime
    preferred: bool = False


class ExternalLinkPolicyError(ValueError):
    code = "INVALID_EXTERNAL_LINK"

    def __init__(self, message: str):
        super().__init__(message)


class ExternalLinkPolicy:
    def validate(self, link: ExternalLink) -> ExternalLink:
        try:
            parsed = urlsplit(link.url)
            hostname = parsed.hostname
        except ValueError as error:
            raise ExternalLinkPolicyError("External link URL is malformed.") from error
        if parsed.scheme != "https" or not parsed.netloc or not hostname:
            raise ExternalLinkPolicyError("External links must be absolute HTTPS URLs with a hostname.")
        return link

    def filter_valid(self, links: tuple[ExternalLink, ...] | list[ExternalLink]) -> tuple[ExternalLink, ...]:
        valid: list[ExternalLink] = []
        for link in links:
            try:
                valid.append(self.validate(link))
            except ExternalLinkPolicyError:
                continue
        return tuple(valid)


class PreferredPostingSelector:
    _availability_rank = {"available": 4, "unknown": 3, "uncertain": 2, "unavailable": 1}
    _source_rank = {"company_careers": 4, "job_board": 3, "professional_network": 2, "other": 1}

    def select(self, links: tuple[ExternalLink, ...] | list[ExternalLink]) -> tuple[ExternalLink, ...]:
        if not links:
            return ()
        newest = max(
            links,
            key=lambda link: (
                self._availability_rank[link.availability],
                self._source_rank[link.source_type],
                self._utc(link.observed_at),
            ),
        )
        tied = [
            link
            for link in links
            if (
                self._availability_rank[link.availability],
                self._source_rank[link.source_type],
                self._utc(link.observed_at),
            )
            == (
                self._availability_rank[newest.availability],
                self._source_rank[newest.source_type],
                self._utc(newest.observed_at),
            )
        ]
        preferred = min(tied, key=lambda link: link.posting_id)
        return tuple(replace(link, preferred=link is preferred) for link in links)

    @staticmethod
    def _utc(value: datetime) -> datetime:
        return (value if value.tzinfo is not None else value.replace(tzinfo=UTC)).astimezone(UTC)
