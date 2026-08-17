from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal, cast

ApplicationLifecycle = Literal[
    "draft",
    "ready",
    "submitted",
    "interviewing",
    "offer",
    "accepted",
    "rejected",
    "withdrawn",
]
TerminalLifecycle = Literal["accepted", "rejected", "withdrawn"]
ApplicationMaterialKind = Literal["cv", "cover_letter", "other"]

_LIFECYCLES = frozenset(
    {
        "draft",
        "ready",
        "submitted",
        "interviewing",
        "offer",
        "accepted",
        "rejected",
        "withdrawn",
    }
)
_TERMINAL_LIFECYCLES: frozenset[TerminalLifecycle] = frozenset({"accepted", "rejected", "withdrawn"})
_MATERIAL_KINDS = frozenset({"cv", "cover_letter", "other"})


class ApplicationCaseError(ValueError):
    """Base error for invalid Application Case or Material values."""


class ApplicationCaseConflictError(ApplicationCaseError):
    """Error for lifecycle changes that conflict with the current case state."""


@dataclass(frozen=True)
class ApplicationLifecycleEvent:
    previous_status: ApplicationLifecycle | None
    resulting_status: ApplicationLifecycle
    occurred_at: datetime


@dataclass(frozen=True)
class ApplicationCase:
    id: str
    opportunity_id: str
    lifecycle: ApplicationLifecycle
    created_at: datetime
    updated_at: datetime
    lifecycle_events: tuple[ApplicationLifecycleEvent, ...]


@dataclass(frozen=True)
class ApplicationMaterial:
    id: str
    application_case_id: str
    kind: ApplicationMaterialKind
    display_name: str
    revision: int
    created_at: datetime
    updated_at: datetime


def _require_id(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ApplicationCaseError(f"{label} must be nonempty.")


def _lifecycle(value: str) -> ApplicationLifecycle:
    if value not in _LIFECYCLES:
        raise ApplicationCaseError(f"Unsupported application lifecycle: {value!r}.")
    return cast(ApplicationLifecycle, value)


def _material_kind(value: str) -> ApplicationMaterialKind:
    if value not in _MATERIAL_KINDS:
        raise ApplicationCaseError(f"Unsupported application material kind: {value!r}.")
    return cast(ApplicationMaterialKind, value)


def _display_name(value: str) -> str:
    result = value.strip()
    if not result:
        raise ApplicationCaseError("Application material display name must be nonempty.")
    return result


def create_application_case(case_id: str, opportunity_id: str, occurred_at: datetime) -> ApplicationCase:
    _require_id(case_id, "Application Case ID")
    _require_id(opportunity_id, "Opportunity ID")
    event = ApplicationLifecycleEvent(None, "draft", occurred_at)
    return ApplicationCase(case_id, opportunity_id, "draft", occurred_at, occurred_at, (event,))


def change_application_case_lifecycle(
    case: ApplicationCase,
    target_status: str,
    occurred_at: datetime,
) -> ApplicationCase:
    target = _lifecycle(target_status)
    if case.lifecycle in _TERMINAL_LIFECYCLES:
        raise ApplicationCaseConflictError("A terminal Application Case cannot change lifecycle.")
    if target == case.lifecycle:
        raise ApplicationCaseConflictError("Application Case lifecycle is already at the requested status.")
    event = ApplicationLifecycleEvent(case.lifecycle, target, occurred_at)
    return replace(case, lifecycle=target, updated_at=occurred_at, lifecycle_events=case.lifecycle_events + (event,))


def create_application_material(
    material_id: str,
    application_case_id: str,
    kind: str,
    display_name: str,
    occurred_at: datetime,
) -> ApplicationMaterial:
    _require_id(material_id, "Application Material ID")
    _require_id(application_case_id, "Application Case ID")
    material_kind = _material_kind(kind)
    return ApplicationMaterial(
        material_id,
        application_case_id,
        material_kind,
        _display_name(display_name),
        1,
        occurred_at,
        occurred_at,
    )


def revise_application_material(
    material: ApplicationMaterial,
    *,
    display_name: str,
    occurred_at: datetime,
) -> ApplicationMaterial:
    return replace(material, display_name=_display_name(display_name), revision=material.revision + 1, updated_at=occurred_at)
