from __future__ import annotations

from collections.abc import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.domain.map_locations import MapLocationResolution
from vocation.infrastructure.models import MapLocationResolutionModel, WorkLocationModel


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

    def delete(self, work_location_id: str) -> None:
        with self.session_factory.begin() as session:
            self._required_work_location(session, work_location_id)
            model = session.get(MapLocationResolutionModel, work_location_id)
            if model is not None:
                session.delete(model)

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
