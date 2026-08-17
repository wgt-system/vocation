from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, replace
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from vocation.domain.profiles import (
    CandidateProfile,
    Education,
    Language,
    ProfileValidationError,
    ProjectHighlight,
    SearchProfile,
    Skill,
    validate_candidate_profile,
    validate_search_profile,
)
from vocation.infrastructure.profile_models import (
    CandidateProfileRevisionModel,
    SearchProfileModel,
    SearchProfileRevisionModel,
)


class SearchProfileNotFoundError(LookupError):
    pass


class SearchProfileConflictError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def _candidate_from_payload(payload: dict) -> CandidateProfile:
    return CandidateProfile(
        revision=int(payload["revision"]),
        headline=str(payload["headline"]),
        summary=str(payload["summary"]),
        education=tuple(Education(**item) for item in payload.get("education", [])),
        skills=tuple(Skill(**item) for item in payload.get("skills", [])),
        languages=tuple(Language(**item) for item in payload.get("languages", [])),
        experience_summary=str(payload.get("experience_summary", "")),
        projects=tuple(
            ProjectHighlight(
                name=item["name"],
                summary=item["summary"],
                technologies=tuple(item.get("technologies", [])),
            )
            for item in payload.get("projects", [])
        ),
        interests=tuple(payload.get("interests", [])),
    )


def _search_from_payload(payload: dict, *, is_default: bool | None = None) -> SearchProfile:
    return SearchProfile(
        id=str(payload["id"]),
        revision=int(payload["revision"]),
        name=str(payload["name"]),
        description=str(payload["description"]),
        target_roles=tuple(payload.get("target_roles", [])),
        seniority_targets=tuple(payload.get("seniority_targets", [])),
        preferred_technologies=tuple(payload.get("preferred_technologies", [])),
        acceptable_technologies=tuple(payload.get("acceptable_technologies", [])),
        avoided_technologies=tuple(payload.get("avoided_technologies", [])),
        target_locations=tuple(payload.get("target_locations", [])),
        work_models=tuple(payload.get("work_models", [])),  # type: ignore[arg-type]
        relocation_willing=bool(payload.get("relocation_willing", False)),
        employment_types=tuple(payload.get("employment_types", [])),
        preferred_industries=tuple(payload.get("preferred_industries", [])),
        avoided_industries=tuple(payload.get("avoided_industries", [])),
        preferred_company_characteristics=tuple(payload.get("preferred_company_characteristics", [])),
        avoided_company_characteristics=tuple(payload.get("avoided_company_characteristics", [])),
        salary_floor=payload.get("salary_floor"),
        salary_target=payload.get("salary_target"),
        salary_currency=str(payload.get("salary_currency", "EUR")),
        must_haves=tuple(payload.get("must_haves", [])),
        must_not_haves=tuple(payload.get("must_not_haves", [])),
        result_limit=int(payload.get("result_limit", 12)),
        is_default=bool(payload.get("is_default", False) if is_default is None else is_default),
    )


class SqlAlchemyProfileRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get_candidate_profile(self) -> CandidateProfile | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(CandidateProfileRevisionModel).order_by(CandidateProfileRevisionModel.revision.desc()).limit(1)
            )
            return None if model is None else _candidate_from_payload(json.loads(model.payload_json))

    def save_candidate_profile(self, profile: CandidateProfile) -> CandidateProfile:
        with self.session_factory.begin() as session:
            latest = session.scalar(select(func.max(CandidateProfileRevisionModel.revision)))
            next_revision = int(latest or 0) + 1
            saved = replace(profile, revision=next_revision)
            validate_candidate_profile(saved)
            session.add(
                CandidateProfileRevisionModel(
                    revision=next_revision,
                    payload_json=json.dumps(asdict(saved), ensure_ascii=False, sort_keys=True),
                    created_at=utc_now(),
                )
            )
            return saved

    def list_search_profiles(self) -> list[SearchProfile]:
        with self.session_factory() as session:
            models = session.scalars(select(SearchProfileModel).order_by(SearchProfileModel.name, SearchProfileModel.id)).all()
            return [self._current_search_profile(session, model) for model in models]

    def get_search_profile(self, profile_id: str) -> SearchProfile | None:
        with self.session_factory() as session:
            model = session.get(SearchProfileModel, profile_id)
            return None if model is None else self._current_search_profile(session, model)

    def get_default_search_profile(self) -> SearchProfile | None:
        with self.session_factory() as session:
            model = session.scalar(select(SearchProfileModel).where(SearchProfileModel.is_default.is_(True)).limit(1))
            return None if model is None else self._current_search_profile(session, model)

    def create_search_profile(self, profile: SearchProfile) -> SearchProfile:
        saved = replace(profile, revision=1)
        validate_search_profile(saved)
        now = utc_now()
        with self.session_factory.begin() as session:
            if session.get(SearchProfileModel, saved.id) is not None:
                raise SearchProfileConflictError(f"Search Profile '{saved.id}' already exists.")
            if saved.is_default:
                session.execute(update(SearchProfileModel).values(is_default=False))
            model = SearchProfileModel(
                id=saved.id,
                name=saved.name.strip(),
                is_default=saved.is_default,
                current_revision=1,
                created_at=now,
                updated_at=now,
            )
            session.add(model)
            session.add(
                SearchProfileRevisionModel(
                    search_profile_id=saved.id,
                    revision=1,
                    payload_json=json.dumps(asdict(saved), ensure_ascii=False, sort_keys=True),
                    created_at=now,
                )
            )
            try:
                session.flush()
            except IntegrityError as exc:
                raise SearchProfileConflictError(f"Search Profile name '{saved.name}' already exists.") from exc
            return saved

    def revise_search_profile(self, profile_id: str, profile: SearchProfile) -> SearchProfile:
        with self.session_factory.begin() as session:
            model = session.get(SearchProfileModel, profile_id)
            if model is None:
                raise SearchProfileNotFoundError(f"Search Profile '{profile_id}' does not exist.")
            next_revision = model.current_revision + 1
            saved = replace(profile, id=profile_id, revision=next_revision, is_default=model.is_default)
            validate_search_profile(saved)
            model.name = saved.name.strip()
            model.current_revision = next_revision
            model.updated_at = utc_now()
            session.add(
                SearchProfileRevisionModel(
                    search_profile_id=profile_id,
                    revision=next_revision,
                    payload_json=json.dumps(asdict(saved), ensure_ascii=False, sort_keys=True),
                    created_at=model.updated_at,
                )
            )
            try:
                session.flush()
            except IntegrityError as exc:
                raise SearchProfileConflictError(f"Search Profile name '{saved.name}' already exists.") from exc
            return saved

    def set_default_search_profile(self, profile_id: str) -> SearchProfile:
        with self.session_factory.begin() as session:
            model = session.get(SearchProfileModel, profile_id)
            if model is None:
                raise SearchProfileNotFoundError(f"Search Profile '{profile_id}' does not exist.")
            session.execute(update(SearchProfileModel).values(is_default=False))
            model.is_default = True
            model.updated_at = utc_now()
            session.flush()
            return self._current_search_profile(session, model)

    def delete_search_profile(self, profile_id: str) -> None:
        with self.session_factory.begin() as session:
            model = session.get(SearchProfileModel, profile_id)
            if model is None:
                raise SearchProfileNotFoundError(f"Search Profile '{profile_id}' does not exist.")
            session.delete(model)

    @staticmethod
    def _current_search_profile(session: Session, model: SearchProfileModel) -> SearchProfile:
        revision = session.get(SearchProfileRevisionModel, (model.id, model.current_revision))
        if revision is None:
            raise RuntimeError(f"Search Profile '{model.id}' current revision is missing.")
        return _search_from_payload(json.loads(revision.payload_json), is_default=model.is_default)
