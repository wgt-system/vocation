from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Protocol
from uuid import uuid4

from vocation.domain.search_vocabulary import (
    SEARCH_VOCABULARY_KINDS,
    SearchVocabularyEntry,
    SearchVocabularyKind,
    SearchVocabularyValidationError,
    normalize_search_term,
    validate_search_vocabulary_entry,
)


class SearchVocabularyRepository(Protocol):
    def list_entries(
        self,
        *,
        kind: SearchVocabularyKind | None = None,
        include_inactive: bool = False,
    ) -> list[SearchVocabularyEntry]: ...

    def get_entry(self, entry_id: str) -> SearchVocabularyEntry | None: ...

    def find_by_normalized_label(self, kind: SearchVocabularyKind, normalized_label: str) -> SearchVocabularyEntry | None: ...

    def create_entry(self, entry: SearchVocabularyEntry) -> SearchVocabularyEntry: ...

    def update_entry(self, entry: SearchVocabularyEntry) -> SearchVocabularyEntry: ...


class SearchVocabularyService:
    def __init__(
        self,
        repository: SearchVocabularyRepository,
        id_factory: Callable[[], str] = lambda: str(uuid4()),
    ) -> None:
        self.repository = repository
        self.id_factory = id_factory

    def list_entries(
        self,
        *,
        kind: SearchVocabularyKind | None = None,
        include_inactive: bool = False,
        query: str = "",
    ) -> list[SearchVocabularyEntry]:
        if kind is not None and kind not in SEARCH_VOCABULARY_KINDS:
            raise SearchVocabularyValidationError(f"Unsupported search vocabulary kind '{kind}'.")
        entries = self.repository.list_entries(kind=kind, include_inactive=include_inactive)
        normalized_query = normalize_search_term(query)
        if normalized_query:
            entries = [
                entry
                for entry in entries
                if normalized_query in entry.normalized_label
                or any(normalized_query in normalize_search_term(alias) for alias in entry.aliases)
            ]
        return sorted(entries, key=lambda entry: (entry.kind, entry.label.casefold(), entry.id))

    def create_custom(
        self,
        *,
        kind: SearchVocabularyKind,
        label: str,
        aliases: tuple[str, ...] = (),
        group: str | None = None,
    ) -> SearchVocabularyEntry:
        entry = SearchVocabularyEntry(
            id=self.id_factory(),
            kind=kind,
            label=label.strip(),
            aliases=tuple(alias.strip() for alias in aliases),
            group=group.strip() if group is not None else None,
            is_active=True,
            is_custom=True,
        )
        validate_search_vocabulary_entry(entry)
        if self.repository.find_by_normalized_label(kind, entry.normalized_label) is not None:
            raise SearchVocabularyValidationError(f"Search vocabulary already contains '{entry.label}' for kind '{kind}'.")
        return self.repository.create_entry(entry)

    def update(
        self,
        entry_id: str,
        *,
        label: str | None = None,
        aliases: tuple[str, ...] | None = None,
        group: str | None = None,
        group_supplied: bool = False,
        is_active: bool | None = None,
    ) -> SearchVocabularyEntry:
        current = self.repository.get_entry(entry_id)
        if current is None:
            raise LookupError("Search vocabulary entry not found.")

        next_label = current.label if label is None else label.strip()
        next_group = current.group
        if group_supplied:
            next_group = group.strip() if group is not None else None
        updated = replace(
            current,
            label=next_label,
            aliases=current.aliases if aliases is None else tuple(alias.strip() for alias in aliases),
            group=next_group,
            is_active=current.is_active if is_active is None else is_active,
        )
        validate_search_vocabulary_entry(updated)
        duplicate = self.repository.find_by_normalized_label(updated.kind, updated.normalized_label)
        if duplicate is not None and duplicate.id != updated.id:
            raise SearchVocabularyValidationError(f"Search vocabulary already contains '{updated.label}' for kind '{updated.kind}'.")
        return self.repository.update_entry(updated)
