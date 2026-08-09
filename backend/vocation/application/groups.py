from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol
from uuid import uuid4

from vocation.domain.groups import GroupType, OpportunityGroup


class OpportunityGroupRepository(Protocol):
    def create(self, group: OpportunityGroup) -> OpportunityGroup: ...
    def edit(self, group_id: str, *, name: str, description: str | None, group_type: GroupType) -> OpportunityGroup: ...
    def delete(self, group_id: str) -> None: ...
    def list(self) -> list[OpportunityGroup]: ...
    def get(self, group_id: str) -> OpportunityGroup | None: ...
    def add_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup: ...
    def remove_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup: ...
    def reorder(self, group_id: str, opportunity_ids: Sequence[str]) -> OpportunityGroup: ...


class OpportunityGroupService:
    def __init__(self, repository: OpportunityGroupRepository, ref_factory: Callable[[], str] | None = None):
        self.repository = repository
        self.ref_factory = ref_factory or (lambda: str(uuid4()))

    def create(self, name: str, description: str | None, group_type: GroupType) -> OpportunityGroup:
        return self.repository.create(OpportunityGroup(self.ref_factory(), name, description, group_type))

    def edit(self, group_id: str, *, name: str, description: str | None, group_type: GroupType) -> OpportunityGroup:
        return self.repository.edit(group_id, name=name, description=description, group_type=group_type)

    def delete(self, group_id: str) -> None:
        self.repository.delete(group_id)

    def list(self) -> list[OpportunityGroup]:
        return self.repository.list()

    def get(self, group_id: str) -> OpportunityGroup | None:
        return self.repository.get(group_id)

    def add_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup:
        return self.repository.add_opportunity(group_id, opportunity_id)

    def remove_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup:
        return self.repository.remove_opportunity(group_id, opportunity_id)

    def reorder(self, group_id: str, opportunity_ids: Sequence[str]) -> OpportunityGroup:
        return self.repository.reorder(group_id, opportunity_ids)
