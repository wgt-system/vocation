from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from vocation.application.criteria import CriteriaService
from vocation.application.ports import PromptRunRepository


@dataclass(frozen=True)
class GeneratedPrompt:
    prompt_run_id: str
    prompt_text: str
    bundle_version: str
    criteria_count: int


class PromptService:
    def __init__(
        self,
        criteria: CriteriaService,
        prompt_runs: PromptRunRepository,
        initial_template_path: Path,
        output_contract_path: Path,
    ):
        self.criteria = criteria
        self.prompt_runs = prompt_runs
        self.initial_template_path = initial_template_path
        self.output_contract_path = output_contract_path

    def generate_initial(self, *, search_profile: str, constraints: list[str], as_of_date: str) -> GeneratedPrompt:
        if not search_profile.strip():
            raise ValueError("Search profile is required.")
        active_criteria = self.criteria.list(active_only=True)
        snapshot = [criterion.as_snapshot() for criterion in active_criteria]
        criteria_text = json.dumps(snapshot, ensure_ascii=False, indent=2)
        template = self.initial_template_path.read_text(encoding="utf-8")
        output_contract = self.output_contract_path.read_text(encoding="utf-8")
        prompt_text = (
            template.replace("{{SEARCH_PROFILE}}", search_profile.strip())
            .replace("{{CONSTRAINTS}}", json.dumps(constraints, ensure_ascii=False, indent=2))
            .replace("{{AS_OF_DATE}}", as_of_date)
            .replace("{{ACTIVE_ASSESSMENT_CRITERIA}}", criteria_text)
            .replace("{{OUTPUT_CONTRACT}}", output_contract)
        )
        prompt_run_id = self.prompt_runs.save_initial(
            search_profile=search_profile.strip(),
            constraints=constraints,
            as_of_date=as_of_date,
            criteria_snapshot=snapshot,
            prompt_text=prompt_text,
        )
        return GeneratedPrompt(prompt_run_id, prompt_text, "1.0", len(snapshot))
