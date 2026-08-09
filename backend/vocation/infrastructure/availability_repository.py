from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.application.availability_imports import AvailabilityImportPlan, AvailabilityImportRepository
from vocation.domain.research_bundle import ImportIssue, ImportReport
from vocation.infrastructure.models import AvailabilityObservationModel, ImportIssueModel, ResearchImportModel


def _uuid() -> str:
    return str(uuid4())


class SqlAlchemyAvailabilityImportRepository(AvailabilityImportRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def find_applied_availability(self, fingerprint: str) -> ImportReport | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(ResearchImportModel).where(
                    ResearchImportModel.fingerprint == fingerprint,
                    ResearchImportModel.import_kind == "availability_check",
                    ResearchImportModel.status == "applied",
                )
            )
            return self._report(model) if model else None

    def record_rejected_availability(
        self, *, bundle_id: str | None, fingerprint: str | None, bundle_version: str | None, warnings: list[str], issues: list[ImportIssue]
    ) -> ImportReport:
        import_id = _uuid()
        with self.session_factory.begin() as session:
            session.add(
                ResearchImportModel(
                    id=import_id,
                    bundle_id=bundle_id,
                    bundle_version=bundle_version,
                    import_kind="availability_check",
                    fingerprint=fingerprint,
                    status="rejected",
                    counts_json="{}",
                    warnings_json=json.dumps(warnings, ensure_ascii=False),
                )
            )
            for issue in issues:
                session.add(
                    ImportIssueModel(
                        id=_uuid(), import_id=import_id, severity=issue.severity, code=issue.code, path=issue.path, message=issue.message
                    )
                )
        return ImportReport(
            import_id,
            "rejected",
            bundle_id,
            fingerprint,
            warnings=warnings,
            issues=issues,
            bundle_version=bundle_version,
            import_kind="availability_check",
        )

    def apply_availability(self, bundle: dict, plan: AvailabilityImportPlan, fingerprint: str) -> ImportReport:
        import_id = _uuid()
        counts = {"availability_observations_created": len(plan.observations)}
        warnings = bundle["warnings"]
        with self.session_factory.begin() as session:
            session.add(
                ResearchImportModel(
                    id=import_id,
                    bundle_id=bundle["bundle_id"],
                    bundle_version="1.0",
                    import_kind="availability_check",
                    prompt_context_ref=plan.prompt_context_ref,
                    fingerprint=fingerprint,
                    status="applied",
                    applied_at=datetime.now(UTC),
                    counts_json=json.dumps(counts),
                    warnings_json=json.dumps(warnings, ensure_ascii=False),
                )
            )
            session.flush()
            for planned in plan.observations:
                observation = planned.observation
                session.add(
                    AvailabilityObservationModel(
                        id=_uuid(),
                        import_id=import_id,
                        bundle_local_id=planned.bundle_local_id,
                        posting_id=observation.posting_id,
                        result=observation.result,
                        observed_at=observation.observed_at,
                        evidence_summary=observation.evidence_summary,
                        recorded_at=datetime.now(UTC),
                    )
                )
        return ImportReport(
            import_id,
            "applied",
            bundle["bundle_id"],
            fingerprint,
            counts,
            warnings,
            bundle_version="1.0",
            prompt_context_ref=plan.prompt_context_ref,
            import_kind="availability_check",
        )

    @staticmethod
    def _report(model: ResearchImportModel) -> ImportReport:
        return ImportReport(
            import_id=model.id,
            status=model.status,
            bundle_id=model.bundle_id,
            fingerprint=model.fingerprint,
            counts=json.loads(model.counts_json),
            warnings=json.loads(model.warnings_json),
            issues=[ImportIssue(issue.code, issue.message, issue.path, issue.severity) for issue in model.issues],
            bundle_version=model.bundle_version,
            prompt_context_ref=model.prompt_context_ref,
            import_kind=model.import_kind,
        )
