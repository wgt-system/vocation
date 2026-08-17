from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict
from uuid import uuid4

from sqlalchemy.orm import Session

from vocation.domain.profiles import CandidateProfile, SearchProfile
from vocation.domain.research_bundle import canonical_fingerprint, canonical_json
from vocation.infrastructure.models import PromptContextSnapshotModel, PromptRunModel, ResearchImportModel


class SqlAlchemyInitialResearchRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save(
        self,
        *,
        search_profile: SearchProfile,
        candidate_profile: CandidateProfile | None,
        research_scope: dict,
        as_of_date: str,
        criteria_snapshot: list[dict],
        prompt_text: str,
    ) -> tuple[str, str]:
        prompt_run_id = str(uuid4())
        prompt_context_ref = str(uuid4())
        context = {
            "type": "initial_market_research",
            "as_of_date": as_of_date,
            "search_profile": {
                "id": search_profile.id,
                "revision": search_profile.revision,
                "snapshot": asdict(search_profile),
            },
            "candidate_profile": (
                {
                    "revision": candidate_profile.revision,
                    "snapshot": asdict(candidate_profile),
                }
                if candidate_profile is not None
                else None
            ),
            "research_scope": research_scope,
        }
        fingerprint = canonical_fingerprint(
            {
                "prompt_context_ref": prompt_context_ref,
                "context": context,
            }
        )
        with self.session_factory.begin() as session:
            session.add(
                PromptContextSnapshotModel(
                    prompt_context_ref=prompt_context_ref,
                    scope_type="initial_market_research",
                    as_of_date=as_of_date,
                    scope_json=canonical_json(context),
                    fingerprint=fingerprint,
                )
            )
            session.add(
                PromptRunModel(
                    id=prompt_run_id,
                    prompt_type="initial_market_research",
                    prompt_version="2.0",
                    bundle_version="1.0",
                    search_profile=search_profile.name,
                    prompt_context_ref=prompt_context_ref,
                    constraints_json=json.dumps(research_scope["constraints"], ensure_ascii=False),
                    as_of_date=as_of_date,
                    criteria_snapshot_json=json.dumps(criteria_snapshot, ensure_ascii=False),
                    prompt_text=prompt_text,
                )
            )
        return prompt_run_id, prompt_context_ref

    def context_ref_for_prompt_run(self, prompt_run_id: str) -> str | None:
        with self.session_factory() as session:
            model = session.get(PromptRunModel, prompt_run_id)
            return None if model is None else model.prompt_context_ref

    def link_import(self, import_id: str, prompt_context_ref: str) -> None:
        with self.session_factory.begin() as session:
            model = session.get(ResearchImportModel, import_id)
            if model is None:
                raise LookupError(import_id)
            model.prompt_context_ref = prompt_context_ref
