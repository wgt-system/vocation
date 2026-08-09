from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from vocation.application.ports import PromptRunRepository
from vocation.application.prompt_market import PromptMarketRepository
from vocation.domain.prompt_market import PromptMarket


@dataclass(frozen=True)
class GeneratedAvailabilityPrompt:
    prompt_run_id: str
    prompt_context_ref: str
    prompt_type: str
    prompt_version: str
    bundle_kind: str
    bundle_version: str
    research_scope: dict[str, Any]
    prompt_text: str


class AvailabilityPromptService:
    def __init__(
        self,
        prompt_market: PromptMarketRepository,
        prompt_runs: PromptRunRepository,
        template_path: Path,
        schema_path: Path,
        ref_factory: Callable[[], str] = lambda: str(uuid4()),
    ) -> None:
        self.prompt_market = prompt_market
        self.prompt_runs = prompt_runs
        self.template_path = template_path
        self.schema_path = schema_path
        self.ref_factory = ref_factory

    def generate(self, *, as_of_date: str, posting_ids: list[str]) -> GeneratedAvailabilityPrompt:
        if not posting_ids or len(posting_ids) != len(set(posting_ids)):
            raise ValueError("Posting IDs must be nonempty and unique.")
        market = self.prompt_market.load_market()
        postings = {posting.subject_id: posting for posting in market.postings}
        companies = {company.subject_id: company for company in market.companies}
        opportunities = {opportunity.subject_id: opportunity for opportunity in market.opportunities}
        selected = []
        for posting_id in posting_ids:
            posting = postings.get(posting_id)
            if posting is None:
                raise ValueError(f"Unknown Posting '{posting_id}'.")
            selected.append(posting)

        included_companies = {posting.company_id for posting in selected}
        included_opportunities = {posting.opportunity_id for posting in selected}
        refs = {("company", company_id): self.ref_factory() for company_id in sorted(included_companies)}
        refs.update({("opportunity", opportunity_id): self.ref_factory() for opportunity_id in sorted(included_opportunities)})
        refs.update({("posting", posting.subject_id): self.ref_factory() for posting in selected})
        scope = {
            "type": "availability_check",
            "as_of_date": as_of_date,
            "selected_correlation_refs": [refs[("posting", posting.subject_id)] for posting in selected],
        }
        context = self._context(market, selected, companies, opportunities, refs, scope, self.ref_factory())
        template = self.template_path.read_text(encoding="utf-8")
        prompt_text = template.replace("{{PROMPT_CONTEXT}}", json.dumps(context, ensure_ascii=False, indent=2)).replace(
            "{{OUTPUT_SCHEMA}}", self.schema_path.read_text(encoding="utf-8")
        )
        prompt_context_ref = context["prompt_context_ref"]
        prompt_run_id, prompt_context_ref = self.prompt_runs.save_availability(
            as_of_date=as_of_date,
            research_scope=scope,
            prompt_context_ref=prompt_context_ref,
            subject_mappings=[
                {
                    "correlation_ref": refs[subject],
                    "subject_type": subject[0],
                    "subject_id": subject[1],
                    "is_target": subject[0] == "posting",
                }
                for subject in refs
            ],
            prompt_text=prompt_text,
        )
        return GeneratedAvailabilityPrompt(
            prompt_run_id, prompt_context_ref, "availability_check", "1.0", "availability_check", "1.0", scope, prompt_text
        )

    def _context(self, market: PromptMarket, selected, companies, opportunities, refs, scope, context_ref: str) -> dict[str, Any]:
        return {
            "prompt_context_ref": context_ref,
            "research_scope": scope,
            "known_subjects": {
                "companies": [
                    {"correlation_ref": refs[("company", company_id)], "name": companies[company_id].name, "is_target": False}
                    for company_id in sorted({posting.company_id for posting in selected})
                ],
                "opportunities": [
                    {
                        "correlation_ref": refs[("opportunity", opportunity_id)],
                        "company_correlation_ref": refs[("company", opportunities[opportunity_id].company_id)],
                        "title": opportunities[opportunity_id].title,
                        "is_target": False,
                    }
                    for opportunity_id in sorted({posting.opportunity_id for posting in selected})
                ],
                "postings": [
                    {
                        "correlation_ref": refs[("posting", posting.subject_id)],
                        "company_correlation_ref": refs[("company", posting.company_id)],
                        "opportunity_correlation_ref": refs[("opportunity", posting.opportunity_id)],
                        "title": posting.title,
                        "external_posting_id": posting.external_posting_id,
                        "canonical_url": posting.canonical_url,
                        "published_at": posting.published_at,
                        "observed_at": posting.observed_at.isoformat().replace("+00:00", "Z"),
                        "is_target": True,
                    }
                    for posting in selected
                ],
            },
        }
