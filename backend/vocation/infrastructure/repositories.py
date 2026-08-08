from __future__ import annotations

import json
from collections.abc import Callable
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from vocation.domain.criteria import AssessmentCriterion
from vocation.infrastructure.models import (
    AssessmentCriterionModel,
    ExternalAssessmentModel,
    PersonalAssessmentModel,
    PromptRunModel,
)


class SqlAlchemyCriteriaRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @staticmethod
    def _domain(model: AssessmentCriterionModel) -> AssessmentCriterion:
        return AssessmentCriterion(
            criterion_id=model.criterion_id,
            display_name=model.display_name,
            description=model.description,
            value_type=model.value_type,
            numeric_min=model.numeric_min,
            numeric_max=model.numeric_max,
            allowed_values=tuple(json.loads(model.allowed_values_json)),
            applicable_subject_type=model.applicable_subject_type,
            active=model.active,
            display_order=model.display_order,
            revision=model.revision,
        )

    def list(self, *, active_only: bool = False) -> list[AssessmentCriterion]:
        with self.session_factory() as session:
            statement = select(AssessmentCriterionModel)
            if active_only:
                statement = statement.where(AssessmentCriterionModel.active.is_(True))
            models = session.scalars(statement.order_by(AssessmentCriterionModel.display_order)).all()
            return [self._domain(model) for model in models]

    def get(self, criterion_id: str) -> AssessmentCriterion | None:
        with self.session_factory() as session:
            model = session.get(AssessmentCriterionModel, criterion_id)
            return self._domain(model) if model else None

    def create(self, criterion: AssessmentCriterion) -> AssessmentCriterion:
        with self.session_factory.begin() as session:
            session.add(self._model(criterion))
        return criterion

    def update(self, criterion: AssessmentCriterion) -> AssessmentCriterion:
        with self.session_factory.begin() as session:
            model = session.get(AssessmentCriterionModel, criterion.criterion_id)
            if model is None:
                raise LookupError(criterion.criterion_id)
            self._apply(model, criterion)
        return criterion

    def set_active(self, criterion_id: str, active: bool) -> AssessmentCriterion:
        with self.session_factory.begin() as session:
            model = session.get(AssessmentCriterionModel, criterion_id)
            if model is None:
                raise LookupError(criterion_id)
            model.active = active
            model.revision += 1
        result = self.get(criterion_id)
        assert result is not None
        return result

    def reorder(self, criterion_ids: list[str]) -> list[AssessmentCriterion]:
        with self.session_factory.begin() as session:
            for index, criterion_id in enumerate(criterion_ids, start=1):
                model = session.get(AssessmentCriterionModel, criterion_id)
                if model is None:
                    raise LookupError(criterion_id)
                model.display_order = index * 10
        return self.list()

    def is_referenced(self, criterion_id: str) -> bool:
        with self.session_factory() as session:
            count = session.scalar(
                select(func.count()).select_from(ExternalAssessmentModel).where(ExternalAssessmentModel.criterion_id == criterion_id)
            )
            personal_count = session.scalar(
                select(func.count()).select_from(PersonalAssessmentModel).where(PersonalAssessmentModel.criterion_id == criterion_id)
            )
            return bool(count or personal_count)

    @staticmethod
    def _model(criterion: AssessmentCriterion) -> AssessmentCriterionModel:
        model = AssessmentCriterionModel(criterion_id=criterion.criterion_id)
        SqlAlchemyCriteriaRepository._apply(model, criterion)
        return model

    @staticmethod
    def _apply(model: AssessmentCriterionModel, criterion: AssessmentCriterion) -> None:
        model.display_name = criterion.display_name
        model.description = criterion.description
        model.value_type = criterion.value_type
        model.numeric_min = criterion.numeric_min
        model.numeric_max = criterion.numeric_max
        model.allowed_values_json = json.dumps(list(criterion.allowed_values), ensure_ascii=False)
        model.applicable_subject_type = criterion.applicable_subject_type
        model.active = criterion.active
        model.display_order = criterion.display_order
        model.revision = criterion.revision


class SqlAlchemyPromptRunRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def save_initial(
        self,
        *,
        search_profile: str,
        constraints: list[str],
        as_of_date: str,
        criteria_snapshot: list[dict],
        prompt_text: str,
    ) -> str:
        prompt_run_id = str(uuid4())
        with self.session_factory.begin() as session:
            session.add(
                PromptRunModel(
                    id=prompt_run_id,
                    search_profile=search_profile,
                    constraints_json=json.dumps(constraints, ensure_ascii=False),
                    as_of_date=as_of_date,
                    criteria_snapshot_json=json.dumps(criteria_snapshot, ensure_ascii=False),
                    prompt_text=prompt_text,
                )
            )
        return prompt_run_id
