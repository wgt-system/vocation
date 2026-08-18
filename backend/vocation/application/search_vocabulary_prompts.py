from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from vocation.application.search_vocabulary import SearchVocabularyRepository
from vocation.domain.search_vocabulary import SearchVocabularyKind, normalize_search_term

REFRESHABLE_KINDS: tuple[SearchVocabularyKind, ...] = ("role", "technology", "industry")


@dataclass(frozen=True, slots=True)
class GeneratedSearchVocabularyPrompt:
    prompt_version: str
    as_of_date: str
    kinds: tuple[SearchVocabularyKind, ...]
    prompt_text: str


@dataclass(frozen=True, slots=True)
class SearchVocabularyProposal:
    kind: SearchVocabularyKind
    label: str
    aliases: tuple[str, ...]
    group: str | None
    reason: str
    source_urls: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReviewedSearchVocabularyProposal:
    proposal: SearchVocabularyProposal
    already_known_entry_id: str | None


class SearchVocabularyPromptService:
    prompt_version = "1.0"

    def __init__(self, repository: SearchVocabularyRepository, template_path: Path) -> None:
        self.repository = repository
        self.template_path = template_path

    def generate(
        self,
        *,
        as_of_date: str,
        kinds: tuple[SearchVocabularyKind, ...] = REFRESHABLE_KINDS,
    ) -> GeneratedSearchVocabularyPrompt:
        if not kinds:
            raise ValueError("At least one refreshable vocabulary kind is required.")
        unsupported = [kind for kind in kinds if kind not in REFRESHABLE_KINDS]
        if unsupported:
            raise ValueError("Catalog refresh supports only role, technology and industry vocabularies.")
        if len(set(kinds)) != len(kinds):
            raise ValueError("Catalog refresh vocabulary kinds must be unique.")

        catalog: dict[str, list[dict[str, object]]] = {}
        for kind in kinds:
            catalog[kind] = [
                {
                    "label": entry.label,
                    "aliases": list(entry.aliases),
                    "group": entry.group,
                }
                for entry in self.repository.list_entries(kind=kind, include_inactive=False)
            ]

        template = self.template_path.read_text(encoding="utf-8")
        prompt = (
            template.replace("{{PROMPT_VERSION}}", self.prompt_version)
            .replace("{{AS_OF_DATE}}", as_of_date)
            .replace("{{KINDS}}", ", ".join(kinds))
            .replace(
                "{{CURRENT_CATALOG_JSON}}",
                json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True),
            )
        )
        return GeneratedSearchVocabularyPrompt(
            prompt_version=self.prompt_version,
            as_of_date=as_of_date,
            kinds=kinds,
            prompt_text=prompt,
        )

    def review_proposals(self, proposals: tuple[SearchVocabularyProposal, ...]) -> list[ReviewedSearchVocabularyProposal]:
        reviewed: list[ReviewedSearchVocabularyProposal] = []
        for proposal in proposals:
            if proposal.kind not in REFRESHABLE_KINDS:
                raise ValueError("Catalog refresh proposals support only role, technology and industry.")
            label = proposal.label.strip()
            if not label:
                raise ValueError("Catalog proposal labels must be nonempty.")
            normalized = normalize_search_term(label)
            known = self.repository.find_by_normalized_label(proposal.kind, normalized)
            reviewed.append(
                ReviewedSearchVocabularyProposal(
                    proposal=proposal,
                    already_known_entry_id=None if known is None else known.id,
                )
            )
        return reviewed
