from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from vocation.application.application_cases import (
    ApplicationCaseNotFoundError,
    ApplicationMaterialNotFoundError,
    OpportunityNotFoundError,
)
from vocation.domain.application_cases import (
    ApplicationCase,
    ApplicationCaseConflictError,
    ApplicationLifecycleEvent,
    ApplicationMaterial,
)
from vocation.infrastructure.models import (
    ApplicationCaseLifecycleEventModel,
    ApplicationCaseModel,
    ApplicationMaterialModel,
    ApplicationMaterialRevisionModel,
    OpportunityModel,
)


class SqlAlchemyApplicationCaseRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, case_id: str) -> ApplicationCase | None:
        with self.session_factory() as session:
            model = session.get(ApplicationCaseModel, case_id)
            return None if model is None else self._case_domain(model, session)

    def list_for_opportunity(self, opportunity_id: str) -> list[ApplicationCase]:
        with self.session_factory() as session:
            if session.get(OpportunityModel, opportunity_id) is None:
                raise OpportunityNotFoundError(opportunity_id)
            models = session.scalars(
                select(ApplicationCaseModel)
                .where(ApplicationCaseModel.opportunity_id == opportunity_id)
                .order_by(ApplicationCaseModel.created_at, ApplicationCaseModel.id)
            ).all()
            return [self._case_domain(model, session) for model in models]

    def create_case(self, case: ApplicationCase) -> ApplicationCase:
        with self.session_factory.begin() as session:
            if session.get(OpportunityModel, case.opportunity_id) is None:
                raise OpportunityNotFoundError(case.opportunity_id)
            active = session.scalar(
                select(ApplicationCaseModel.id)
                .where(
                    ApplicationCaseModel.opportunity_id == case.opportunity_id,
                    ApplicationCaseModel.lifecycle.not_in(("accepted", "rejected", "withdrawn")),
                )
                .limit(1)
            )
            if active is not None:
                raise ApplicationCaseConflictError(f"Opportunity '{case.opportunity_id}' already has an active Application Case.")
            session.add(
                ApplicationCaseModel(
                    id=case.id,
                    opportunity_id=case.opportunity_id,
                    lifecycle=case.lifecycle,
                    created_at=case.created_at,
                    updated_at=case.updated_at,
                )
            )
            session.add(self._event_model(case.id, 1, case.lifecycle_events[0]))
            try:
                session.flush()
            except IntegrityError as error:
                raise ApplicationCaseConflictError("Application Case conflicts with existing state.") from error
            return case

    def persist_lifecycle_change(self, case: ApplicationCase, event: ApplicationLifecycleEvent) -> ApplicationCase:
        with self.session_factory.begin() as session:
            model = session.get(ApplicationCaseModel, case.id)
            if model is None:
                raise ApplicationCaseNotFoundError(case.id)
            if model.lifecycle != event.previous_status:
                raise ApplicationCaseConflictError("Application Case lifecycle changed concurrently.")
            next_sequence = session.scalar(
                select(func.coalesce(func.max(ApplicationCaseLifecycleEventModel.sequence), 0) + 1).where(
                    ApplicationCaseLifecycleEventModel.application_case_id == case.id
                )
            )
            model.lifecycle = case.lifecycle
            model.updated_at = case.updated_at
            session.add(self._event_model(case.id, int(next_sequence), event))
            session.flush()
            return self._case_domain(model, session)

    def get_material(self, material_id: str) -> ApplicationMaterial | None:
        with self.session_factory() as session:
            model = session.get(ApplicationMaterialModel, material_id)
            return None if model is None else self._material_domain(model, session)

    def list_materials(self, case_id: str) -> list[ApplicationMaterial]:
        with self.session_factory() as session:
            if session.get(ApplicationCaseModel, case_id) is None:
                raise ApplicationCaseNotFoundError(case_id)
            models = session.scalars(
                select(ApplicationMaterialModel)
                .where(ApplicationMaterialModel.application_case_id == case_id)
                .order_by(ApplicationMaterialModel.created_at, ApplicationMaterialModel.id)
            ).all()
            return [self._material_domain(model, session) for model in models]

    def create_material(self, material: ApplicationMaterial) -> ApplicationMaterial:
        with self.session_factory.begin() as session:
            if session.get(ApplicationCaseModel, material.application_case_id) is None:
                raise ApplicationCaseNotFoundError(material.application_case_id)
            session.add(
                ApplicationMaterialModel(
                    id=material.id,
                    application_case_id=material.application_case_id,
                    kind=material.kind,
                    created_at=material.created_at,
                )
            )
            session.add(
                ApplicationMaterialRevisionModel(
                    material_id=material.id,
                    revision=material.revision,
                    display_name=material.display_name,
                    updated_at=material.updated_at,
                )
            )
            session.flush()
            return material

    def persist_material_revision(self, material: ApplicationMaterial) -> ApplicationMaterial:
        with self.session_factory.begin() as session:
            model = session.get(ApplicationMaterialModel, material.id)
            if model is None:
                raise ApplicationMaterialNotFoundError(material.id)
            if model.application_case_id != material.application_case_id:
                raise ApplicationMaterialNotFoundError(material.id)
            current_revision = session.scalar(
                select(func.max(ApplicationMaterialRevisionModel.revision)).where(
                    ApplicationMaterialRevisionModel.material_id == material.id
                )
            )
            if current_revision != material.revision - 1:
                raise ApplicationCaseConflictError("Application Material revision is stale.")
            session.add(
                ApplicationMaterialRevisionModel(
                    material_id=material.id,
                    revision=material.revision,
                    display_name=material.display_name,
                    updated_at=material.updated_at,
                )
            )
            session.flush()
            return material

    @staticmethod
    def _event_model(case_id: str, sequence: int, event: ApplicationLifecycleEvent) -> ApplicationCaseLifecycleEventModel:
        return ApplicationCaseLifecycleEventModel(
            application_case_id=case_id,
            sequence=sequence,
            previous_status=event.previous_status,
            resulting_status=event.resulting_status,
            occurred_at=event.occurred_at,
        )

    @classmethod
    def _case_domain(cls, model: ApplicationCaseModel, session: Session) -> ApplicationCase:
        events = session.scalars(
            select(ApplicationCaseLifecycleEventModel)
            .where(ApplicationCaseLifecycleEventModel.application_case_id == model.id)
            .order_by(ApplicationCaseLifecycleEventModel.sequence)
        ).all()
        return ApplicationCase(
            id=model.id,
            opportunity_id=model.opportunity_id,
            lifecycle=model.lifecycle,  # type: ignore[arg-type]
            created_at=cls._aware(model.created_at),
            updated_at=cls._aware(model.updated_at),
            lifecycle_events=tuple(
                ApplicationLifecycleEvent(item.previous_status, item.resulting_status, cls._aware(item.occurred_at))  # type: ignore[arg-type]
                for item in events
            ),
        )

    @staticmethod
    def _material_domain(model: ApplicationMaterialModel, session: Session) -> ApplicationMaterial:
        revision = session.scalar(
            select(ApplicationMaterialRevisionModel)
            .where(ApplicationMaterialRevisionModel.material_id == model.id)
            .order_by(ApplicationMaterialRevisionModel.revision.desc())
            .limit(1)
        )
        if revision is None:
            raise ApplicationMaterialNotFoundError(model.id)
        return ApplicationMaterial(
            id=model.id,
            application_case_id=model.application_case_id,
            kind=model.kind,  # type: ignore[arg-type]
            display_name=revision.display_name,
            revision=revision.revision,
            created_at=SqlAlchemyApplicationCaseRepository._aware(model.created_at),
            updated_at=SqlAlchemyApplicationCaseRepository._aware(revision.updated_at),
        )

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


__all__ = ["ApplicationCaseConflictError", "SqlAlchemyApplicationCaseRepository"]
