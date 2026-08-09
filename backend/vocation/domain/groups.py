from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GroupType = Literal["general", "application_wave"]


@dataclass(frozen=True)
class OpportunityGroupMembership:
    opportunity_id: str
    position: int
    opportunity_title: str | None = None
    company_name: str | None = None


@dataclass(frozen=True)
class OpportunityGroup:
    id: str
    name: str
    description: str | None
    group_type: GroupType
    memberships: tuple[OpportunityGroupMembership, ...] = ()
