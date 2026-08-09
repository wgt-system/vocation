from __future__ import annotations

from collections.abc import Callable, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from vocation.domain.groups import GroupType, OpportunityGroup, OpportunityGroupMembership
from vocation.infrastructure.models import OpportunityGroupMembershipModel, OpportunityGroupModel, OpportunityModel


class OpportunityGroupNotFoundError(LookupError):
    pass


class OpportunityNotFoundError(LookupError):
    pass


class OpportunityGroupValidationError(ValueError):
    pass


class OpportunityGroupMembershipError(ValueError):
    pass


class SqlAlchemyOpportunityGroupRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def create(self, group: OpportunityGroup) -> OpportunityGroup:
        self._validate_group_values(group.name, group.group_type)
        with self.session_factory.begin() as session:
            if session.get(OpportunityGroupModel, group.id) is not None:
                raise OpportunityGroupValidationError(f"Opportunity Group '{group.id}' already exists.")
            model = OpportunityGroupModel(
                id=group.id,
                name=group.name,
                description=group.description,
                group_type=group.group_type,
            )
            session.add(model)
            session.flush()
            return self._domain(model, session)

    def edit(self, group_id: str, *, name: str, description: str | None, group_type: GroupType) -> OpportunityGroup:
        self._validate_group_values(name, group_type)
        with self.session_factory.begin() as session:
            model = self._required_group(session, group_id)
            model.name = name
            model.description = description
            model.group_type = group_type
            session.flush()
            return self._domain(model, session)

    def delete(self, group_id: str) -> None:
        with self.session_factory.begin() as session:
            model = self._required_group(session, group_id)
            session.delete(model)

    def list(self) -> list[OpportunityGroup]:
        with self.session_factory() as session:
            models = session.scalars(select(OpportunityGroupModel).order_by(OpportunityGroupModel.id)).all()
            return [self._domain(model, session) for model in models]

    def get(self, group_id: str) -> OpportunityGroup | None:
        with self.session_factory() as session:
            model = session.get(OpportunityGroupModel, group_id)
            return None if model is None else self._domain(model, session)

    def add_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup:
        with self.session_factory.begin() as session:
            group = self._required_group(session, group_id)
            self._required_opportunity(session, opportunity_id)
            existing = session.get(OpportunityGroupMembershipModel, (group_id, opportunity_id))
            if existing is not None:
                raise OpportunityGroupMembershipError(f"Opportunity '{opportunity_id}' is already in Group '{group_id}'.")
            next_position = session.scalar(
                select(func.coalesce(func.max(OpportunityGroupMembershipModel.position), -1) + 1).where(
                    OpportunityGroupMembershipModel.group_id == group_id
                )
            )
            session.add(
                OpportunityGroupMembershipModel(
                    group_id=group_id,
                    opportunity_id=opportunity_id,
                    position=int(next_position),
                )
            )
            session.flush()
            return self._domain(group, session)

    def remove_opportunity(self, group_id: str, opportunity_id: str) -> OpportunityGroup:
        with self.session_factory.begin() as session:
            group = self._required_group(session, group_id)
            self._required_opportunity(session, opportunity_id)
            memberships = self._ordered_memberships(session, group_id)
            member = next((item for item in memberships if item.opportunity_id == opportunity_id), None)
            if member is None:
                raise OpportunityGroupMembershipError(f"Opportunity '{opportunity_id}' is not in Group '{group_id}'.")
            session.delete(member)
            session.flush()
            remaining = [item.opportunity_id for item in memberships if item.opportunity_id != opportunity_id]
            self._rewrite_positions(session, group_id, remaining)
            return self._domain(group, session)

    def reorder(self, group_id: str, opportunity_ids: Sequence[str]) -> OpportunityGroup:
        requested = list(opportunity_ids)
        if len(requested) != len(set(requested)):
            raise OpportunityGroupMembershipError("Reorder must not contain duplicate Opportunity IDs.")
        with self.session_factory.begin() as session:
            group = self._required_group(session, group_id)
            for opportunity_id in requested:
                self._required_opportunity(session, opportunity_id)
            existing = {item.opportunity_id for item in self._ordered_memberships(session, group_id)}
            if set(requested) != existing:
                raise OpportunityGroupMembershipError("Reorder must contain exactly the existing Group members.")
            self._rewrite_positions(session, group_id, requested)
            return self._domain(group, session)

    @staticmethod
    def _validate_group_values(name: str, group_type: str) -> None:
        if not name.strip():
            raise OpportunityGroupValidationError("Opportunity Group name must be nonempty.")
        if group_type not in {"general", "application_wave"}:
            raise OpportunityGroupValidationError("Opportunity Group type is invalid.")

    @staticmethod
    def _required_group(session: Session, group_id: str) -> OpportunityGroupModel:
        group = session.get(OpportunityGroupModel, group_id)
        if group is None:
            raise OpportunityGroupNotFoundError(f"Opportunity Group '{group_id}' does not exist.")
        return group

    @staticmethod
    def _required_opportunity(session: Session, opportunity_id: str) -> OpportunityModel:
        opportunity = session.get(OpportunityModel, opportunity_id)
        if opportunity is None:
            raise OpportunityNotFoundError(f"Opportunity '{opportunity_id}' does not exist.")
        return opportunity

    @staticmethod
    def _ordered_memberships(session: Session, group_id: str) -> list[OpportunityGroupMembershipModel]:
        return list(
            session.scalars(
                select(OpportunityGroupMembershipModel)
                .where(OpportunityGroupMembershipModel.group_id == group_id)
                .order_by(OpportunityGroupMembershipModel.position)
            ).all()
        )

    @classmethod
    def _rewrite_positions(cls, session: Session, group_id: str, opportunity_ids: Sequence[str]) -> None:
        memberships = {item.opportunity_id: item for item in cls._ordered_memberships(session, group_id)}
        offset = len(opportunity_ids) + 1
        for position, opportunity_id in enumerate(opportunity_ids):
            memberships[opportunity_id].position = offset + position
        session.flush()
        for position, opportunity_id in enumerate(opportunity_ids):
            memberships[opportunity_id].position = position
        session.flush()

    @classmethod
    def _domain(cls, model: OpportunityGroupModel, session: Session) -> OpportunityGroup:
        memberships = cls._ordered_memberships(session, model.id)
        return OpportunityGroup(
            id=model.id,
            name=model.name,
            description=model.description,
            group_type=model.group_type,  # type: ignore[arg-type]
            memberships=tuple(OpportunityGroupMembership(item.opportunity_id, item.position) for item in memberships),
        )
