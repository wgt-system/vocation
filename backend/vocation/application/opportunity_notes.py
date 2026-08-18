from __future__ import annotations

from typing import Protocol


class OpportunityNoteRepository(Protocol):
    def get(self, opportunity_id: str) -> dict | None: ...
    def save(self, opportunity_id: str, content: str) -> dict: ...
    def clear(self, opportunity_id: str) -> None: ...


class OpportunityNoteService:
    def __init__(self, repository: OpportunityNoteRepository):
        self.repository = repository

    def get(self, opportunity_id: str) -> dict | None:
        return self.repository.get(opportunity_id)

    def save(self, opportunity_id: str, content: str) -> dict | None:
        normalized = content.strip()
        if not normalized:
            self.repository.clear(opportunity_id)
            return None
        return self.repository.save(opportunity_id, normalized)
