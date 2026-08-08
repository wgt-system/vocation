from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.update_import import PromptContextSnapshot, PromptContextSubject, SubjectType
from vocation.infrastructure.models import PromptContextSnapshotModel, PromptContextSubjectModel


class SqlAlchemyPromptContextSnapshotRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, prompt_context_ref: str) -> PromptContextSnapshot | None:
        with self.session_factory() as session:
            model = session.get(PromptContextSnapshotModel, prompt_context_ref)
            if model is None:
                return None
            subjects = session.scalars(
                select(PromptContextSubjectModel)
                .where(PromptContextSubjectModel.prompt_context_ref == prompt_context_ref)
                .order_by(PromptContextSubjectModel.correlation_ref)
            ).all()
            return PromptContextSnapshot(
                prompt_context_ref=model.prompt_context_ref,
                scope_type=model.scope_type,
                as_of_date=date.fromisoformat(model.as_of_date),
                scope_json=json.loads(model.scope_json),
                subjects=tuple(
                    PromptContextSubject(
                        item.correlation_ref,
                        cast(SubjectType, item.subject_type),
                        item.subject_id,
                        item.is_target,
                    )
                    for item in subjects
                ),
                created_at=model.created_at,
            )
