from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.research_bundle import PostingIdentity
from vocation.infrastructure.models import PostingModel


class SqlAlchemyPostingIdentityRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get_posting(self, posting_id: str) -> PostingIdentity | None:
        with self.session_factory() as session:
            return self._identity(session.get(PostingModel, posting_id))

    def find_by_stable_key(self, stable_key: str) -> PostingIdentity | None:
        with self.session_factory() as session:
            return self._identity(session.scalar(select(PostingModel).where(PostingModel.stable_key == stable_key)))

    def find_by_normalized_canonical_url(self, normalized_url: str) -> PostingIdentity | None:
        with self.session_factory() as session:
            return self._identity(session.scalar(select(PostingModel).where(PostingModel.canonical_url == normalized_url)))

    @staticmethod
    def _identity(model: PostingModel | None) -> PostingIdentity | None:
        if model is None:
            return None
        return PostingIdentity(model.id, model.stable_key, model.canonical_url)
