from __future__ import annotations

from collections.abc import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.application.map import MapGroupMembership, MapLocationContext
from vocation.domain.availability import AvailabilityObservation
from vocation.domain.map_locations import MapLocationResolution
from vocation.infrastructure.models import (
    AvailabilityObservationModel,
    CompanyModel,
    MapLocationResolutionModel,
    OpportunityGroupMembershipModel,
    OpportunityGroupModel,
    OpportunityModel,
    PostingModel,
    WorkLocationModel,
)


class WorkLocationNotFoundError(LookupError):
    pass


class MapLocationResolutionValidationError(ValueError):
    pass


class SqlAlchemyMapLocationResolutionRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, work_location_id: str) -> MapLocationResolution | None:
        with self.session_factory() as session:
            self._required_work_location(session, work_location_id)
            model = session.get(MapLocationResolutionModel, work_location_id)
            return None if model is None else self._domain(model)

    def set(self, resolution: MapLocationResolution) -> MapLocationResolution:
        self._validate_resolution(resolution)
        with self.session_factory.begin() as session:
            self._required_work_location(session, resolution.work_location_id)
            model = session.get(MapLocationResolutionModel, resolution.work_location_id)
            if model is None:
                model = MapLocationResolutionModel(work_location_id=resolution.work_location_id)
                session.add(model)
            model.latitude = resolution.latitude
            model.longitude = resolution.longitude
            model.resolution_source = resolution.resolution_source
            model.provider_key = resolution.provider_key
            model.resolved_at = resolution.resolved_at
            model.resolved_query = resolution.resolved_query
            session.flush()
            return self._domain(model)

    def set_resolution(self, resolution: MapLocationResolution) -> MapLocationResolution:
        return self.set(resolution)

    def delete(self, work_location_id: str) -> None:
        with self.session_factory.begin() as session:
            self._required_work_location(session, work_location_id)
            model = session.get(MapLocationResolutionModel, work_location_id)
            if model is not None:
                session.delete(model)

    def delete_resolution(self, work_location_id: str) -> None:
        self.delete(work_location_id)

    def list(self, work_location_ids: Iterable[str]) -> list[MapLocationResolution]:
        ids = list(dict.fromkeys(work_location_ids))
        with self.session_factory() as session:
            existing_ids = set(session.scalars(select(WorkLocationModel.id).where(WorkLocationModel.id.in_(ids))).all())
            missing_id = next((work_location_id for work_location_id in ids if work_location_id not in existing_ids), None)
            if missing_id is not None:
                raise WorkLocationNotFoundError(f"Work Location '{missing_id}' does not exist.")
            models = session.scalars(
                select(MapLocationResolutionModel)
                .where(MapLocationResolutionModel.work_location_id.in_(ids))
                .order_by(MapLocationResolutionModel.work_location_id)
            ).all()
            return [self._domain(model) for model in models]

    def list_locations(self) -> list[MapLocationContext]:
        with self.session_factory() as session:
            locations = session.scalars(select(WorkLocationModel).order_by(WorkLocationModel.id)).all()
            return [self._context(session, location) for location in locations]

    def get_location(self, work_location_id: str) -> MapLocationContext | None:
        with self.session_factory() as session:
            location = session.get(WorkLocationModel, work_location_id)
            return None if location is None else self._context(session, location)

    def list_locations_for_opportunities(self, opportunity_ids: Iterable[str]) -> list[MapLocationContext]:
        ids = list(dict.fromkeys(opportunity_ids))
        if not ids:
            return []
        with self.session_factory() as session:
            locations = session.scalars(
                select(WorkLocationModel).where(WorkLocationModel.opportunity_id.in_(ids)).order_by(WorkLocationModel.id)
            ).all()
            return [self._context(session, location) for location in locations]

    @classmethod
    def _context(cls, session: Session, location: WorkLocationModel) -> MapLocationContext:
        opportunity = session.get(OpportunityModel, location.opportunity_id)
        assert opportunity is not None
        company = session.get(CompanyModel, opportunity.company_id)
        resolution_model = session.get(MapLocationResolutionModel, location.id)
        posting_ids = session.scalars(select(PostingModel.id).where(PostingModel.opportunity_id == opportunity.id)).all()
        observations = session.scalars(
            select(AvailabilityObservationModel)
            .where(AvailabilityObservationModel.posting_id.in_(posting_ids))
            .order_by(
                AvailabilityObservationModel.observed_at,
                AvailabilityObservationModel.recorded_at,
                AvailabilityObservationModel.id,
            )
        ).all()
        observations_by_posting: dict[str, list[AvailabilityObservation]] = {posting_id: [] for posting_id in posting_ids}
        for row in observations:
            observations_by_posting[row.posting_id].append(
                AvailabilityObservation(
                    row.id,
                    row.posting_id,
                    row.result,  # type: ignore[arg-type]
                    row.observed_at,
                    row.recorded_at,
                    row.evidence_summary,
                )
            )
        groups = session.execute(
            select(OpportunityGroupModel.id, OpportunityGroupModel.name, OpportunityGroupModel.group_type)
            .join(OpportunityGroupMembershipModel, OpportunityGroupMembershipModel.group_id == OpportunityGroupModel.id)
            .where(OpportunityGroupMembershipModel.opportunity_id == opportunity.id)
            .order_by(OpportunityGroupModel.id)
        ).all()
        return MapLocationContext(
            work_location_id=location.id,
            opportunity_id=opportunity.id,
            company_id=opportunity.company_id,
            title=opportunity.canonical_title,
            company_name=company.canonical_name,
            label=location.label,
            city=location.city,
            region=location.region,
            country_code=location.country_code,
            precision=location.precision,
            tracking_status=opportunity.tracking_status,
            resolution=None if resolution_model is None else cls._domain(resolution_model),
            availability_observations=tuple(tuple(observations_by_posting[posting_id]) for posting_id in posting_ids),
            groups=tuple(MapGroupMembership(row.id, row.name, row.group_type) for row in groups),
        )

    @staticmethod
    def _validate_resolution(resolution: MapLocationResolution) -> None:
        if not -90 <= resolution.latitude <= 90:
            raise MapLocationResolutionValidationError("Latitude must be between -90 and 90.")
        if not -180 <= resolution.longitude <= 180:
            raise MapLocationResolutionValidationError("Longitude must be between -180 and 180.")
        if resolution.resolution_source not in {"manual", "geocoder"}:
            raise MapLocationResolutionValidationError("Resolution source is invalid.")
        if not resolution.resolved_query.strip():
            raise MapLocationResolutionValidationError("Resolved query must be nonempty.")
        if resolution.resolution_source == "manual" and resolution.provider_key is not None:
            raise MapLocationResolutionValidationError("Manual resolutions cannot have a provider key.")
        if resolution.resolution_source == "geocoder" and (resolution.provider_key is None or not resolution.provider_key.strip()):
            raise MapLocationResolutionValidationError("Geocoder resolutions require a nonempty provider key.")

    @staticmethod
    def _required_work_location(session: Session, work_location_id: str) -> WorkLocationModel:
        work_location = session.get(WorkLocationModel, work_location_id)
        if work_location is None:
            raise WorkLocationNotFoundError(f"Work Location '{work_location_id}' does not exist.")
        return work_location

    @staticmethod
    def _domain(model: MapLocationResolutionModel) -> MapLocationResolution:
        return MapLocationResolution(
            work_location_id=model.work_location_id,
            latitude=model.latitude,
            longitude=model.longitude,
            resolution_source=model.resolution_source,  # type: ignore[arg-type]
            provider_key=model.provider_key,
            resolved_at=model.resolved_at,
            resolved_query=model.resolved_query,
        )
