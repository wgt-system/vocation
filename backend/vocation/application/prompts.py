from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from vocation.application.criteria import CriteriaService
from vocation.application.ports import PromptRunRepository
from vocation.application.prompt_market import PromptMarketRepository
from vocation.domain.prompt_market import PromptMarket


@dataclass(frozen=True)
class GeneratedPrompt:
    prompt_run_id: str
    prompt_text: str
    bundle_version: str
    criteria_count: int


@dataclass(frozen=True)
class GeneratedUpdatePrompt:
    prompt_run_id: str
    prompt_context_ref: str
    prompt_type: str
    prompt_version: str
    bundle_version: str
    research_scope: dict
    prompt_text: str
    criteria_count: int


class PromptService:
    def __init__(
        self,
        criteria: CriteriaService,
        prompt_runs: PromptRunRepository,
        initial_template_path: Path,
        output_contract_path: Path,
        prompt_market: PromptMarketRepository,
        update_template_dir: Path,
        update_schema_path: Path,
        ref_factory: Callable[[], str] = lambda: str(uuid4()),
    ):
        self.criteria = criteria
        self.prompt_runs = prompt_runs
        self.initial_template_path = initial_template_path
        self.output_contract_path = output_contract_path
        self.prompt_market = prompt_market
        self.update_template_dir = update_template_dir
        self.update_schema_path = update_schema_path
        self.ref_factory = ref_factory

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

    def generate_update(
        self,
        *,
        mode: str,
        as_of_date: str,
        selected_ids: list[str] | None = None,
        gap_requests: list[dict] | None = None,
    ) -> GeneratedUpdatePrompt:
        if mode not in {"full_update", "company_update", "opportunity_update", "gap_filling"}:
            raise ValueError("Unsupported update mode.")
        market = self.prompt_market.load_market()
        scope, included, targets, requested_pairs, selected_order = self._build_scope(
            market, mode, selected_ids or [], gap_requests or []
        )
        scope["as_of_date"] = as_of_date
        prompt_context_ref = self.ref_factory()
        correlation_refs = {
            subject: self.ref_factory() for subject in sorted(included, key=lambda value: (value[0], value[1]))
        }
        context = self._render_context(
            market,
            scope,
            included,
            targets,
            correlation_refs,
            requested_pairs,
            gap_requests or [],
            selected_order,
            prompt_context_ref,
        )
        active_criteria = self.criteria.list(active_only=True)
        if mode == "gap_filling":
            requested_criteria = {
                request["criterion_id"]
                for request in gap_requests or []
                if request.get("criterion_id") is not None
            }
            active_criteria = [criterion for criterion in active_criteria if criterion.criterion_id in requested_criteria]
        criteria_snapshot = [criterion.as_snapshot() for criterion in active_criteria]
        template = (self.update_template_dir / f"{mode.replace('_', '-')}.md").read_text(encoding="utf-8")
        prompt_text = (
            template.replace("{{PROMPT_CONTEXT}}", json.dumps(context, ensure_ascii=False, indent=2))
            .replace("{{ACTIVE_ASSESSMENT_CRITERIA}}", json.dumps(criteria_snapshot, ensure_ascii=False, indent=2))
            .replace("{{OUTPUT_SCHEMA}}", self.update_schema_path.read_text(encoding="utf-8"))
        )
        prompt_run_id, prompt_context_ref = self.prompt_runs.save_update(
            prompt_type=mode,
            as_of_date=as_of_date,
            research_scope=scope,
            prompt_context_ref=prompt_context_ref,
            subject_mappings=[
                {
                    "correlation_ref": correlation_refs[subject],
                    "subject_type": subject[0],
                    "subject_id": subject[1],
                    "is_target": subject in targets,
                }
                for subject in sorted(included, key=lambda value: (value[0], value[1]))
            ],
            criteria_snapshot=criteria_snapshot,
            prompt_text=prompt_text,
        )
        return GeneratedUpdatePrompt(
            prompt_run_id,
            prompt_context_ref,
            mode,
            "1.0",
            "2.0",
            scope,
            prompt_text,
            len(criteria_snapshot),
        )

    def _build_scope(
        self,
        market: PromptMarket,
        mode: str,
        selected_ids: list[str],
        gap_requests: list[dict],
    ) -> tuple[
        dict,
        set[tuple[str, str]],
        set[tuple[str, str]],
        set[tuple[str, str, str | None, str | None]],
        list[tuple[str, str]],
    ]:
        companies = {company.subject_id: company for company in market.companies}
        opportunities = {opportunity.subject_id: opportunity for opportunity in market.opportunities}
        postings = {posting.subject_id: posting for posting in market.postings}
        included: set[tuple[str, str]] = set()
        targets: set[tuple[str, str]] = set()
        requested_pairs: set[tuple[str, str, str | None, str | None]] = set()
        selected_order: list[tuple[str, str]] = []
        if mode == "full_update":
            targets = {
                ("company", company_id) for company_id in companies
            } | {("opportunity", opportunity_id) for opportunity_id in opportunities} | {
                ("posting", posting_id) for posting_id in postings
            }
            included = set(targets)
            scope = {"type": mode, "as_of_date": ""}
        elif mode == "company_update":
            self._require_ids(selected_ids, "Company")
            for company_id in selected_ids:
                if company_id not in companies:
                    raise ValueError(f"Unknown Company '{company_id}'.")
                targets.add(("company", company_id))
                if ("company", company_id) not in selected_order:
                    selected_order.append(("company", company_id))
            for opportunity in market.opportunities:
                if ("company", opportunity.company_id) in targets:
                    targets.add(("opportunity", opportunity.subject_id))
            for posting in market.postings:
                if ("opportunity", posting.opportunity_id) in targets:
                    targets.add(("posting", posting.subject_id))
            included = set(targets)
            scope = {"type": mode, "as_of_date": "", "selected_correlation_refs": []}
        elif mode == "opportunity_update":
            self._require_ids(selected_ids, "Opportunity")
            for opportunity_id in selected_ids:
                opportunity = opportunities.get(opportunity_id)
                if opportunity is None:
                    raise ValueError(f"Unknown Opportunity '{opportunity_id}'.")
                targets.add(("opportunity", opportunity_id))
                if ("opportunity", opportunity_id) not in selected_order:
                    selected_order.append(("opportunity", opportunity_id))
                included.add(("company", opportunity.company_id))
            for posting in market.postings:
                if ("opportunity", posting.opportunity_id) in targets:
                    targets.add(("posting", posting.subject_id))
            included.update(targets)
            scope = {"type": mode, "as_of_date": "", "selected_correlation_refs": []}
        else:
            if not gap_requests:
                raise ValueError("Gap Filling requires at least one request.")
            request_keys: set[tuple[str, str, str | None, str | None]] = set()
            for request in gap_requests:
                subject_type = request.get("subject_type")
                subject_id = request.get("subject_id")
                observation_type = request.get("observation_type")
                criterion_id = request.get("criterion_id")
                key = (subject_type, subject_id, observation_type, criterion_id)
                if key in request_keys:
                    raise ValueError("Gap Filling requests must be unique.")
                request_keys.add(key)
                if subject_type not in {"company", "opportunity", "posting"}:
                    raise ValueError("Gap Filling subject type is invalid.")
                if (observation_type is None) == (criterion_id is None):
                    raise ValueError("Gap Filling requests need exactly one evidence kind.")
                if subject_type == "company" and subject_id not in companies:
                    raise ValueError(f"Unknown Company '{subject_id}'.")
                if subject_type == "opportunity" and subject_id not in opportunities:
                    raise ValueError(f"Unknown Opportunity '{subject_id}'.")
                if subject_type == "posting" and subject_id not in postings:
                    raise ValueError(f"Unknown Posting '{subject_id}'.")
                if observation_type is not None and observation_type not in {
                    "technology_requirement",
                    "task",
                    "seniority",
                    "experience_requirement",
                    "work_model",
                    "salary",
                }:
                    raise ValueError("Gap Filling observation type is invalid.")
                if criterion_id is not None:
                    criterion = self.criteria.get(criterion_id)
                    if criterion is None or not criterion.active:
                        raise ValueError(f"Unknown or inactive criterion '{criterion_id}'.")
                    if criterion.applicable_subject_type != subject_type:
                        raise ValueError("Gap Filling criterion subject type does not match.")
                target = (subject_type, subject_id)
                targets.add(target)
                if target not in selected_order:
                    selected_order.append(target)
                requested_pairs.add(key)
                if subject_type == "opportunity":
                    included.add(("company", opportunities[subject_id].company_id))
                elif subject_type == "posting":
                    posting = postings[subject_id]
                    included.update({("company", posting.company_id), ("opportunity", posting.opportunity_id)})
            included.update(targets)
            scope = {"type": mode, "as_of_date": "", "selected_correlation_refs": [], "requests": []}
        return scope, included, targets, requested_pairs, selected_order

    @staticmethod
    def _require_ids(selected_ids: list[str], subject_name: str) -> None:
        if not selected_ids:
            raise ValueError(f"{subject_name} selection must not be empty.")

    def _render_context(
        self,
        market: PromptMarket,
        scope: dict,
        included: set[tuple[str, str]],
        targets: set[tuple[str, str]],
        correlation_refs: dict[tuple[str, str], str],
        requested_pairs: set[tuple[str, str, str | None, str | None]],
        gap_requests: list[dict],
        selected_order: list[tuple[str, str]],
        prompt_context_ref: str,
    ) -> dict:
        scope = json.loads(json.dumps(scope))
        if scope["type"] != "full_update":
            scope["selected_correlation_refs"] = [
                correlation_refs[subject]
                for subject in selected_order
            ]
        if scope["type"] == "gap_filling":
            scope["requests"] = [
                {
                    "correlation_ref": correlation_refs[(request["subject_type"], request["subject_id"])],
                    "subject_type": request["subject_type"],
                    **{
                        key: request[key]
                        for key in ("observation_type", "criterion_id")
                        if key in request
                    },
                }
                for request in gap_requests
            ]
        companies = {company.subject_id: company for company in market.companies}
        opportunities = {opportunity.subject_id: opportunity for opportunity in market.opportunities}
        postings = {posting.subject_id: posting for posting in market.postings}
        context = {
            "prompt_context_ref": prompt_context_ref,
            "research_scope": scope,
            "known_subjects": {"companies": [], "opportunities": [], "postings": []},
            "latest_observations": [],
            "latest_external_assessments": [],
            "unresolved_duplicate_cases": [],
        }
        for company_id, company in companies.items():
            key = ("company", company_id)
            if key in included:
                context["known_subjects"]["companies"].append(
                    {
                        "correlation_ref": correlation_refs[key],
                        "name": company.name,
                        "source_url": company.source_url,
                        "is_target": key in targets,
                    }
                )
        for opportunity_id, opportunity in opportunities.items():
            key = ("opportunity", opportunity_id)
            if key in included:
                context["known_subjects"]["opportunities"].append(
                    {
                        "correlation_ref": correlation_refs[key],
                        "company_correlation_ref": correlation_refs[("company", opportunity.company_id)],
                        "title": opportunity.title,
                        "work_locations": [location.__dict__ for location in opportunity.locations],
                        "source_url": opportunity.source_url,
                        "is_target": key in targets,
                    }
                )
        for posting_id, posting in postings.items():
            key = ("posting", posting_id)
            if key in included:
                context["known_subjects"]["postings"].append(
                    {
                        "correlation_ref": correlation_refs[key],
                        "company_correlation_ref": correlation_refs[("company", posting.company_id)],
                        "opportunity_correlation_ref": correlation_refs[("opportunity", posting.opportunity_id)],
                        "title": posting.title,
                        "external_posting_id": posting.external_posting_id,
                        "canonical_url": posting.canonical_url,
                        "published_at": posting.published_at,
                        "observed_at": posting.observed_at.isoformat(),
                        "is_target": key in targets,
                    }
                )
        allowed_observations = self._latest_observations(market, targets, requested_pairs)
        context["latest_observations"] = [
            {
                "subject_correlation_ref": correlation_refs[(item.subject_type, item.subject_id)],
                "type": item.observation_type,
                "value": item.value,
                "observed_at": item.observed_at.isoformat(),
                "confidence": item.confidence,
                "evidence_summary": item.evidence_summary,
                "source_url": item.source_url,
            }
            for item in allowed_observations
        ]
        context["latest_external_assessments"] = [
            {
                "subject_correlation_ref": correlation_refs[(item.subject_type, item.subject_id)],
                "criterion_id": item.criterion_id,
                "value": item.value,
                "created_at": item.created_at.isoformat(),
                "reasoning": item.reasoning,
                "source_urls": list(item.source_urls),
            }
            for item in self._latest_assessments(market, targets, requested_pairs)
        ]
        if scope["type"] != "gap_filling":
            context["unresolved_duplicate_cases"] = [
                {
                    "subject_type": case.subject_type,
                    "left_subject_correlation_ref": correlation_refs[(case.subject_type, case.left_subject_id)],
                    "right_subject_correlation_ref": correlation_refs[(case.subject_type, case.right_subject_id)],
                    "evidence_summary": case.evidence_summary,
                    "confidence": case.confidence,
                    "source_urls": list(case.source_urls),
                }
                for case in market.duplicate_cases
                if (case.subject_type, case.left_subject_id) in targets
                and (case.subject_type, case.right_subject_id) in targets
            ]
        return context

    @staticmethod
    def _latest_observations(
        market: PromptMarket,
        targets: set[tuple[str, str]],
        requested_pairs: set[tuple[str, str, str | None, str | None]],
    ):
        latest = {}
        for item in market.observations:
            subject = (item.subject_type, item.subject_id)
            if subject not in targets:
                continue
            if requested_pairs and (
                item.subject_type,
                item.subject_id,
                item.observation_type,
                None,
            ) not in requested_pairs:
                continue
            key = (item.subject_type, item.subject_id, item.observation_type)
            if key not in latest or item.observed_at > latest[key].observed_at:
                latest[key] = item
        return [latest[key] for key in sorted(latest)]

    @staticmethod
    def _latest_assessments(
        market: PromptMarket,
        targets: set[tuple[str, str]],
        requested_pairs: set[tuple[str, str, str | None, str | None]],
    ):
        latest = {}
        for item in market.assessments:
            subject = (item.subject_type, item.subject_id)
            if subject not in targets:
                continue
            if requested_pairs and (
                item.subject_type,
                item.subject_id,
                None,
                item.criterion_id,
            ) not in requested_pairs:
                continue
            key = (item.subject_type, item.subject_id, item.criterion_id)
            if key not in latest or item.created_at > latest[key].created_at:
                latest[key] = item
        return [latest[key] for key in sorted(latest)]
