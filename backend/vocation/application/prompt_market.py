from __future__ import annotations

from typing import Protocol

from vocation.domain.prompt_market import PromptMarket


class PromptMarketRepository(Protocol):
    def load_market(self) -> PromptMarket: ...
