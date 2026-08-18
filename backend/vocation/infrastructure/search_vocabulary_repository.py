from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.search_vocabulary import SearchVocabularyEntry, SearchVocabularyKind
from vocation.infrastructure.search_vocabulary_models import SearchVocabularyEntryModel


class SqlAlchemySearchVocabularyRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory

    def list_entries(
        self,
        *,
        kind: SearchVocabularyKind | None = None,
        include_inactive: bool = False,
    ) -> list[SearchVocabularyEntry]:
        with self.session_factory() as session:
            statement = select(SearchVocabularyEntryModel)
            if kind is not None:
                statement = statement.where(SearchVocabularyEntryModel.kind == kind)
            if not include_inactive:
                statement = statement.where(SearchVocabularyEntryModel.is_active.is_(True))
            statement = statement.order_by(
                SearchVocabularyEntryModel.kind,
                SearchVocabularyEntryModel.normalized_label,
                SearchVocabularyEntryModel.id,
            )
            return [self._to_domain(model) for model in session.scalars(statement)]

    def get_entry(self, entry_id: str) -> SearchVocabularyEntry | None:
        with self.session_factory() as session:
            model = session.get(SearchVocabularyEntryModel, entry_id)
            return None if model is None else self._to_domain(model)

    def find_by_normalized_label(
        self, kind: SearchVocabularyKind, normalized_label: str
    ) -> SearchVocabularyEntry | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(SearchVocabularyEntryModel).where(
                    SearchVocabularyEntryModel.kind == kind,
                    SearchVocabularyEntryModel.normalized_label == normalized_label,
                )
            )
            return None if model is None else self._to_domain(model)

    def create_entry(self, entry: SearchVocabularyEntry) -> SearchVocabularyEntry:
        now = datetime.now(UTC)
        with self.session_factory() as session:
            session.add(
                SearchVocabularyEntryModel(
                    id=entry.id,
                    kind=entry.kind,
                    label=entry.label,
                    normalized_label=entry.normalized_label,
                    aliases_json=json.dumps(list(entry.aliases), ensure_ascii=False),
                    group_name=entry.group,
                    is_active=entry.is_active,
                    is_custom=entry.is_custom,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.commit()
        return entry

    def update_entry(self, entry: SearchVocabularyEntry) -> SearchVocabularyEntry:
        with self.session_factory() as session:
            model = session.get(SearchVocabularyEntryModel, entry.id)
            if model is None:
                raise LookupError("Search vocabulary entry not found.")
            model.label = entry.label
            model.normalized_label = entry.normalized_label
            model.aliases_json = json.dumps(list(entry.aliases), ensure_ascii=False)
            model.group_name = entry.group
            model.is_active = entry.is_active
            model.updated_at = datetime.now(UTC)
            session.commit()
        return entry

    @staticmethod
    def _to_domain(model: SearchVocabularyEntryModel) -> SearchVocabularyEntry:
        aliases = json.loads(model.aliases_json)
        if not isinstance(aliases, list) or not all(isinstance(item, str) for item in aliases):
            raise RuntimeError(f"Invalid aliases payload for search vocabulary entry '{model.id}'.")
        return SearchVocabularyEntry(
            id=model.id,
            kind=model.kind,  # type: ignore[arg-type]
            label=model.label,
            aliases=tuple(aliases),
            group=model.group_name,
            is_active=model.is_active,
            is_custom=model.is_custom,
        )
