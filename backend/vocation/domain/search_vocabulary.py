from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SearchVocabularyKind = Literal["role", "technology", "industry", "seniority", "employment_type"]
SEARCH_VOCABULARY_KINDS: tuple[SearchVocabularyKind, ...] = (
    "role",
    "technology",
    "industry",
    "seniority",
    "employment_type",
)


class SearchVocabularyValidationError(ValueError):
    """Raised when a search-vocabulary mutation violates Vocation rules."""


@dataclass(frozen=True, slots=True)
class SearchVocabularyEntry:
    id: str
    kind: SearchVocabularyKind
    label: str
    aliases: tuple[str, ...] = ()
    group: str | None = None
    is_active: bool = True
    is_custom: bool = False

    @property
    def normalized_label(self) -> str:
        return normalize_search_term(self.label)


def normalize_search_term(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def validate_search_vocabulary_entry(entry: SearchVocabularyEntry) -> None:
    if entry.kind not in SEARCH_VOCABULARY_KINDS:
        raise SearchVocabularyValidationError(f"Unsupported search vocabulary kind '{entry.kind}'.")
    if not entry.label.strip():
        raise SearchVocabularyValidationError("Search vocabulary label must be nonempty.")
    if len(entry.label.strip()) > 160:
        raise SearchVocabularyValidationError("Search vocabulary label must not exceed 160 characters.")

    normalized_aliases: set[str] = set()
    for alias in entry.aliases:
        normalized = normalize_search_term(alias)
        if not normalized:
            raise SearchVocabularyValidationError("Search vocabulary aliases must be nonempty.")
        if normalized == entry.normalized_label:
            raise SearchVocabularyValidationError("Search vocabulary alias must differ from the canonical label.")
        if normalized in normalized_aliases:
            raise SearchVocabularyValidationError("Search vocabulary aliases must be unique.")
        normalized_aliases.add(normalized)

    if entry.group is not None and not entry.group.strip():
        raise SearchVocabularyValidationError("Search vocabulary group must be nonempty when supplied.")
