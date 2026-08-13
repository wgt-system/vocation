from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from vocation.application.application_documents import (
    ApplicationDocumentConflictError,
    StoredApplicationDocument,
)
from vocation.domain.application_cases import ApplicationMaterial, ApplicationMaterialKind
from vocation.domain.application_documents import ApplicationDocument, ApplicationDocumentMediaType
from vocation.infrastructure.models import (
    ApplicationDocumentModel,
    ApplicationMaterialModel,
    ApplicationMaterialRevisionModel,
)


class SqlAlchemyApplicationDocumentRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get(self, document_id: str) -> StoredApplicationDocument | None:
        with self.session_factory() as session:
            model = session.get(ApplicationDocumentModel, document_id)
            return None if model is None else self._stored_domain(model)

    def get_for_material_revision(self, material_id: str, material_revision: int) -> StoredApplicationDocument | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(ApplicationDocumentModel).where(
                    ApplicationDocumentModel.material_id == material_id,
                    ApplicationDocumentModel.material_revision == material_revision,
                )
            )
            return None if model is None else self._stored_domain(model)

    def get_material_revision(self, material_id: str, material_revision: int) -> ApplicationMaterial | None:
        with self.session_factory() as session:
            material = session.get(ApplicationMaterialModel, material_id)
            revision = session.scalar(
                select(ApplicationMaterialRevisionModel).where(
                    ApplicationMaterialRevisionModel.material_id == material_id,
                    ApplicationMaterialRevisionModel.revision == material_revision,
                )
            )
            if material is None or revision is None:
                return None
            return ApplicationMaterial(
                id=material.id,
                application_case_id=material.application_case_id,
                kind=cast(ApplicationMaterialKind, material.kind),
                display_name=revision.display_name,
                revision=revision.revision,
                created_at=self._aware(material.created_at),
                updated_at=self._aware(revision.updated_at),
            )

    def create(self, document: ApplicationDocument, storage_ref: str) -> ApplicationDocument:
        with self.session_factory.begin() as session:
            existing = session.scalar(
                select(ApplicationDocumentModel).where(
                    ApplicationDocumentModel.material_id == document.material_id,
                    ApplicationDocumentModel.material_revision == document.material_revision,
                )
            )
            if existing is not None:
                raise ApplicationDocumentConflictError("An Application Document already exists for this material revision.")
            session.add(
                ApplicationDocumentModel(
                    id=document.id,
                    material_id=document.material_id,
                    material_revision=document.material_revision,
                    original_filename=document.original_filename,
                    media_type=document.media_type,
                    byte_size=document.byte_size,
                    sha256=document.sha256,
                    storage_ref=storage_ref,
                    created_at=document.created_at,
                )
            )
            try:
                session.flush()
            except IntegrityError as error:
                raise ApplicationDocumentConflictError("Application Document conflicts with existing metadata.") from error
            return document

    @classmethod
    def _stored_domain(cls, model: ApplicationDocumentModel) -> StoredApplicationDocument:
        document = ApplicationDocument(
            id=model.id,
            material_id=model.material_id,
            material_revision=model.material_revision,
            original_filename=model.original_filename,
            media_type=cast(ApplicationDocumentMediaType, model.media_type),
            byte_size=model.byte_size,
            sha256=model.sha256,
            created_at=cls._aware(model.created_at),
        )
        return StoredApplicationDocument(document=document, storage_ref=model.storage_ref)

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
