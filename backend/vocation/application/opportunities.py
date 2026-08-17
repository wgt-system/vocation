from __future__ import annotations

from typing import Any, Protocol


class OpportunityReadRepository(Protocol):
    def list(self, *, group_id: str | None = None) -> list[dict[str, Any]]: ...
    def detail(self, opportunity_id: str) -> dict[str, Any] | None: ...


class OpportunityQueryService:
    def __init__(self, repository: OpportunityReadRepository):
        self.repository = repository

    def list(self, *, group_id: str | None = None) -> list[dict[str, Any]]:
        return self.repository.list(group_id=group_id)

    def detail(self, opportunity_id: str) -> dict[str, Any] | None:
        return self.repository.detail(opportunity_id)
