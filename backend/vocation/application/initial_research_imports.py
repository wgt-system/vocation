from __future__ import annotations

import json
from dataclasses import replace
from typing import Protocol

from vocation.application.imports import ImportService
from vocation.domain.research_bundle import ImportIssue, ImportReport, canonical_fingerprint
from vocation.domain.update_import import PromptContextSnapshot


class PromptContextReader(Protocol):
    def get(self, prompt_context_ref: str) -> PromptContextSnapshot | None: ...


class InitialResearchLinkRepository(Protocol):
    def context_ref_for_prompt_run(self, prompt_run_id: str) -> str | None: ...

    def link_import(self, import_id: str, prompt_context_ref: str) -> None: ...


class InitialResearchImportService:
    def __init__(
        self,
        base_imports: ImportService,
        contexts: PromptContextReader,
        links: InitialResearchLinkRepository,
    ):
        self.base_imports = base_imports
        self.contexts = contexts
        self.links = links

    def import_text(self, content: str, *, prompt_run_id: str | None = None) -> ImportReport:
        if not prompt_run_id:
            return self.base_imports.import_text(content)

        context_ref = self.links.context_ref_for_prompt_run(prompt_run_id)
        if context_ref is None:
            return self._reject(content, ImportIssue("UNKNOWN_PROMPT_CONTEXT", "Prompt run does not resolve to a stored context."))
        context = self.contexts.get(context_ref)
        if context is None or context.scope_type != "initial_market_research":
            return self._reject(
                content,
                ImportIssue("UNKNOWN_PROMPT_CONTEXT", "Prompt run is not an Initial Research context."),
            )

        try:
            bundle = json.loads(content)
        except (json.JSONDecodeError, UnicodeError):
            return self.base_imports.import_text(content)
        if not isinstance(bundle, dict) or bundle.get("bundle_version") != "1.0":
            return self._reject(
                content,
                ImportIssue("SCOPE_MISMATCH", "Linked Initial Research imports require Research Bundle 1.0."),
            )
        expected_scope = context.scope_json.get("research_scope")
        if bundle.get("research_scope") != expected_scope:
            return self._reject(
                content,
                ImportIssue(
                    "SCOPE_MISMATCH",
                    "Research Bundle scope does not match the profile-aware prompt context.",
                    "$.research_scope",
                ),
            )

        report = self.base_imports.import_text(content)
        if report.status == "applied":
            self.links.link_import(report.import_id, context_ref)
            return replace(report, prompt_context_ref=context_ref)
        return report

    def _reject(self, content: str, issue: ImportIssue) -> ImportReport:
        bundle_id: str | None = None
        fingerprint: str | None = None
        warnings: list[str] = []
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                raw_bundle_id = parsed.get("bundle_id")
                bundle_id = raw_bundle_id if isinstance(raw_bundle_id, str) else None
                raw_warnings = parsed.get("warnings")
                warnings = raw_warnings if isinstance(raw_warnings, list) and all(isinstance(item, str) for item in raw_warnings) else []
                fingerprint = canonical_fingerprint(parsed)
        except (json.JSONDecodeError, UnicodeError, TypeError, ValueError):
            pass
        return self.base_imports.repository.record_rejected(
            bundle_id=bundle_id,
            fingerprint=fingerprint,
            warnings=warnings,
            issues=[issue],
        )
