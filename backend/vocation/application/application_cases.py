from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from vocation.domain.application_cases import (
    ApplicationCase,
    ApplicationLifecycleEvent,
    ApplicationMaterial,
    change_application_case_lifecycle,
    create_application_case,
    create_application_material,
    revise_application_material,
)


class ApplicationCaseNotFoundError(LookupError):
    """The requested Application Case does not exist."""


class ApplicationMaterialNotFoundError(LookupError):
    """The requested Application Material does not exist."""


class OpportunityNotFoundError(LookupError):
    """The requested Opportunity does not exist."""


class ApplicationCaseRepository(Protocol):
    def get(self, case_id: str) -> ApplicationCase | None: ...
    def list_for_opportunity(self, opportunity_id: str) -> list[ApplicationCase]: ...
    def create_case(self, case: ApplicationCase) -> ApplicationCase: ...
    def persist_lifecycle_change(self, case: ApplicationCase, event: ApplicationLifecycleEvent) -> ApplicationCase: ...
    def get_material(self, material_id: str) -> ApplicationMaterial | None: ...
    def list_materials(self, case_id: str) -> list[ApplicationMaterial]: ...
    def create_material(self, material: ApplicationMaterial) -> ApplicationMaterial: ...
    def persist_material_revision(self, material: ApplicationMaterial) -> ApplicationMaterial: ...


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ApplicationCaseService:
    def __init__(
        self,
        repository: ApplicationCaseRepository,
        ref_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.ref_factory = ref_factory or (lambda: str(uuid4()))
        self.clock = clock or _utc_now

    def create_case(self, opportunity_id: str) -> ApplicationCase:
        case = create_application_case(self.ref_factory(), opportunity_id, self.clock())
        return self.repository.create_case(case)

    def change_lifecycle(self, case_id: str, target_status: str) -> ApplicationCase:
        case = self.repository.get(case_id)
        if case is None:
            raise ApplicationCaseNotFoundError(case_id)
        changed = change_application_case_lifecycle(case, target_status, self.clock())
        return self.repository.persist_lifecycle_change(changed, changed.lifecycle_events[-1])

    def get(self, case_id: str) -> ApplicationCase | None:
        return self.repository.get(case_id)

    def list_for_opportunity(self, opportunity_id: str) -> list[ApplicationCase]:
        return self.repository.list_for_opportunity(opportunity_id)

    def create_material(self, case_id: str, kind: str, display_name: str) -> ApplicationMaterial:
        if self.repository.get(case_id) is None:
            raise ApplicationCaseNotFoundError(case_id)
        material = create_application_material(self.ref_factory(), case_id, kind, display_name, self.clock())
        return self.repository.create_material(material)

    def revise_material(self, material_id: str, display_name: str) -> ApplicationMaterial:
        material = self.repository.get_material(material_id)
        if material is None:
            raise ApplicationMaterialNotFoundError(material_id)
        revised = revise_application_material(material, display_name=display_name, occurred_at=self.clock())
        return self.repository.persist_material_revision(revised)

    def list_materials(self, case_id: str) -> list[ApplicationMaterial]:
        return self.repository.list_materials(case_id)


__all__ = [
    "ApplicationCaseNotFoundError",
    "ApplicationCaseRepository",
    "ApplicationCaseService",
    "ApplicationMaterialNotFoundError",
    "OpportunityNotFoundError",
]
