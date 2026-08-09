from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from vocation.domain.research_bundle import (
    ImportIssue,
    ImportReport,
    normalize_https_url,
    posting_identity,
)
from vocation.domain.update_import import UpdateImportPlan
from vocation.infrastructure.models import (
    CompanyModel,
    DuplicateCaseModel,
    DuplicateCaseSourceReferenceModel,
    ExternalAssessmentModel,
    ImportIssueModel,
    ObservationModel,
    OpportunityModel,
    PostingModel,
    ResearchImportModel,
    SourceModel,
    SourceReferenceModel,
    WorkLocationModel,
)


def _uuid() -> str:
    return str(uuid4())


def _datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


class SqlAlchemyImportRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def find_applied(self, fingerprint: str) -> ImportReport | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(ResearchImportModel).where(
                    ResearchImportModel.fingerprint == fingerprint,
                    ResearchImportModel.status == "applied",
                )
            )
            return self._report(model) if model else None

    def get_report(self, import_id: str) -> ImportReport | None:
        with self.session_factory() as session:
            model = session.get(ResearchImportModel, import_id)
            if model is None:
                return None
            _ = model.issues
            return self._report(model)

    def identity_issues(self, bundle: dict[str, Any]) -> list[ImportIssue]:
        sources = {item["id"]: item for item in bundle["sources"]}
        references = {item["id"]: item for item in bundle["source_references"]}
        issues: list[ImportIssue] = []
        with self.session_factory() as session:
            for index, posting in enumerate(bundle["postings"]):
                reference = references[posting["source_reference_id"]]
                source = sources[reference["source_id"]]
                stable_key = posting_identity(source, reference, posting)
                canonical_url = normalize_https_url(reference["url"])
                existing = session.scalar(
                    select(PostingModel).where(
                        or_(
                            PostingModel.stable_key == stable_key,
                            PostingModel.canonical_url == canonical_url,
                        )
                    )
                )
                if existing:
                    message = (
                        "Posting identity conflicts with an existing posting. The initial-only importer does not merge across bundles."
                    )
                    issues.append(ImportIssue("IDENTITY_CONFLICT", message, f"$.postings[{index}]"))
        return issues

    def record_rejected(
        self,
        *,
        bundle_id: str | None,
        fingerprint: str | None,
        warnings: list[str],
        issues: list[ImportIssue],
    ) -> ImportReport:
        import_id = _uuid()
        with self.session_factory.begin() as session:
            model = ResearchImportModel(
                id=import_id,
                bundle_id=bundle_id,
                fingerprint=fingerprint,
                status="rejected",
                counts_json="{}",
                warnings_json=json.dumps(warnings, ensure_ascii=False),
            )
            session.add(model)
            for issue in issues:
                session.add(
                    ImportIssueModel(
                        id=_uuid(),
                        import_id=import_id,
                        severity=issue.severity,
                        code=issue.code,
                        path=issue.path,
                        message=issue.message,
                    )
                )
        return ImportReport(import_id, "rejected", bundle_id, fingerprint, warnings=warnings, issues=issues)

    def apply(self, bundle: dict[str, Any], fingerprint: str) -> ImportReport:
        import_id = _uuid()
        source_ids = {item["id"]: _uuid() for item in bundle["sources"]}
        reference_ids = {item["id"]: _uuid() for item in bundle["source_references"]}
        company_ids = {item["id"]: _uuid() for item in bundle["companies"]}
        opportunity_ids = {item["id"]: _uuid() for item in bundle["opportunities"]}
        posting_ids = {item["id"]: _uuid() for item in bundle["postings"]}
        subject_ids = {
            "company": company_ids,
            "opportunity": opportunity_ids,
            "posting": posting_ids,
        }
        sources = {item["id"]: item for item in bundle["sources"]}
        references = {item["id"]: item for item in bundle["source_references"]}
        counts = {
            "sources": len(source_ids),
            "source_references": len(reference_ids),
            "companies": len(company_ids),
            "opportunities": len(opportunity_ids),
            "postings": len(posting_ids),
            "observations": len(bundle["observations"]),
            "assessments": len(bundle["assessments"]),
        }
        warnings = bundle["warnings"]

        with self.session_factory.begin() as session:
            session.add(
                ResearchImportModel(
                    id=import_id,
                    bundle_id=bundle["bundle_id"],
                    bundle_version="1.0",
                    fingerprint=fingerprint,
                    status="applied",
                    applied_at=datetime.now(UTC),
                    counts_json=json.dumps(counts),
                    warnings_json=json.dumps(warnings, ensure_ascii=False),
                )
            )
            session.flush()
            for item in bundle["sources"]:
                session.add(
                    SourceModel(
                        id=source_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        name=item["name"],
                        source_type=item["type"],
                        base_url=item.get("base_url"),
                        notes=item.get("notes"),
                    )
                )
            session.flush()
            for item in bundle["source_references"]:
                session.add(
                    SourceReferenceModel(
                        id=reference_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        source_id=source_ids[item["source_id"]],
                        url=item["url"],
                        normalized_url=normalize_https_url(item["url"]),
                        external_reference_id=item.get("external_reference_id"),
                        display_label=item.get("display_label"),
                        observed_at=_datetime(item["observed_at"]),
                    )
                )
            session.flush()
            for item in bundle["companies"]:
                session.add(
                    CompanyModel(
                        id=company_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        canonical_name=item["canonical_name"],
                        alternative_names_json=json.dumps(item.get("alternative_names", []), ensure_ascii=False),
                        source_reference_id=reference_ids[item["source_reference_id"]],
                        observed_at=_datetime(item["observed_at"]),
                        evidence_summary=item.get("evidence_summary"),
                    )
                )
            session.flush()
            for item in bundle["opportunities"]:
                opportunity_id = opportunity_ids[item["id"]]
                session.add(
                    OpportunityModel(
                        id=opportunity_id,
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        company_id=company_ids[item["company_id"]],
                        canonical_title=item["canonical_title"],
                        source_reference_id=reference_ids[item["source_reference_id"]],
                        observed_at=_datetime(item["observed_at"]),
                        evidence_summary=item.get("evidence_summary"),
                    )
                )
                session.flush()
                for location in item["work_locations"]:
                    session.add(
                        WorkLocationModel(
                            id=_uuid(),
                            opportunity_id=opportunity_id,
                            label=location["label"],
                            city=location.get("city"),
                            region=location.get("region"),
                            country_code=location.get("country_code"),
                            precision=location["precision"],
                            source_reference_id=reference_ids[location["source_reference_id"]],
                            observed_at=_datetime(location["observed_at"]),
                            evidence_summary=location.get("evidence_summary"),
                        )
                    )
            session.flush()
            for item in bundle["postings"]:
                reference = references[item["source_reference_id"]]
                source = sources[reference["source_id"]]
                session.add(
                    PostingModel(
                        id=posting_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        company_id=company_ids[item["company_id"]],
                        opportunity_id=opportunity_ids[item["opportunity_id"]],
                        source_reference_id=reference_ids[item["source_reference_id"]],
                        title=item["title"],
                        external_posting_id=item.get("external_posting_id"),
                        stable_key=posting_identity(source, reference, item),
                        canonical_url=normalize_https_url(reference["url"]),
                        published_at=item.get("published_at"),
                        observed_at=_datetime(item["observed_at"]),
                        content_fingerprint=item.get("content_fingerprint"),
                    )
                )
            session.flush()
            for item in bundle["observations"]:
                session.add(
                    ObservationModel(
                        id=_uuid(),
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        subject_type=item["subject_type"],
                        subject_id=subject_ids[item["subject_type"]][item["subject_id"]],
                        observation_type=item["type"],
                        value_json=json.dumps(item["value"], ensure_ascii=False),
                        source_reference_id=reference_ids[item["source_reference_id"]],
                        observed_at=_datetime(item["observed_at"]),
                        confidence=item.get("confidence"),
                        evidence_summary=item.get("evidence_summary"),
                    )
                )
            for item in bundle["assessments"]:
                session.add(
                    ExternalAssessmentModel(
                        id=_uuid(),
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        subject_type=item["subject_type"],
                        subject_id=subject_ids[item["subject_type"]][item["subject_id"]],
                        criterion_id=item["criterion_id"],
                        value_json=json.dumps(item["value"], ensure_ascii=False),
                        origin="external_research",
                        source_reference_ids_json=json.dumps(
                            [reference_ids[reference_id] for reference_id in item["source_reference_ids"]]
                        ),
                        created_at=_datetime(item["created_at"]),
                        reasoning=item.get("reasoning"),
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
        )

    def apply_update(self, bundle: dict[str, Any], plan: UpdateImportPlan, fingerprint: str) -> ImportReport:
        import_id = _uuid()
        source_ids = {item["id"]: _uuid() for item in bundle["sources"]}
        reference_ids = {item["id"]: _uuid() for item in bundle["source_references"]}
        companies = {item["id"]: item for item in bundle["companies"]}
        opportunities = {item["id"]: item for item in bundle["opportunities"]}
        postings = {item["id"]: item for item in bundle["postings"]}
        planned = {
            "company": {item.bundle_local_id: item for item in plan.companies},
            "opportunity": {item.bundle_local_id: item for item in plan.opportunities},
            "posting": {item.bundle_local_id: item for item in plan.postings},
        }
        subjects = {
            subject_type: {item.bundle_local_id: item.subject_id for item in items.values()} for subject_type, items in planned.items()
        }
        counts = {
            "sources_created": len(source_ids),
            "source_references_created": len(reference_ids),
            "companies_created": sum(item.action == "create" for item in plan.companies),
            "companies_reused": sum(item.action == "reuse" for item in plan.companies),
            "opportunities_created": sum(item.action == "create" for item in plan.opportunities),
            "opportunities_reused": sum(item.action == "reuse" for item in plan.opportunities),
            "postings_created": sum(item.action == "create" for item in plan.postings),
            "postings_reused": sum(item.action == "reuse" for item in plan.postings),
            "observations_created": len(bundle["observations"]),
            "assessments_created": len(bundle["assessments"]),
            "duplicate_cases_created": sum(item.action == "create" for item in plan.duplicate_cases),
            "duplicate_cases_reused": sum(item.action == "reuse" for item in plan.duplicate_cases),
        }
        warnings = bundle["warnings"]

        with self.session_factory.begin() as session:
            session.add(
                ResearchImportModel(
                    id=import_id,
                    bundle_id=bundle["bundle_id"],
                    bundle_version="2.0",
                    prompt_context_ref=plan.prompt_context_ref,
                    fingerprint=fingerprint,
                    status="applied",
                    applied_at=datetime.now(UTC),
                    counts_json=json.dumps(counts),
                    warnings_json=json.dumps(warnings, ensure_ascii=False),
                )
            )
            session.flush()
            for item in bundle["sources"]:
                session.add(
                    SourceModel(
                        id=source_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        name=item["name"],
                        source_type=item["type"],
                        base_url=item.get("base_url"),
                        notes=item.get("notes"),
                    )
                )
            session.flush()
            for item in bundle["source_references"]:
                session.add(
                    SourceReferenceModel(
                        id=reference_ids[item["id"]],
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        source_id=source_ids[item["source_id"]],
                        url=item["url"],
                        normalized_url=normalize_https_url(item["url"]),
                        external_reference_id=item.get("external_reference_id"),
                        display_label=item.get("display_label"),
                        observed_at=_datetime(item["observed_at"]),
                    )
                )
            session.flush()
            for item in plan.companies:
                if item.action != "create":
                    continue
                source_reference_id = reference_ids[companies[item.bundle_local_id]["source_reference_id"]]
                company = companies[item.bundle_local_id]
                session.add(
                    CompanyModel(
                        id=item.subject_id,
                        import_id=import_id,
                        bundle_local_id=item.bundle_local_id,
                        canonical_name=company["canonical_name"],
                        alternative_names_json=json.dumps(company.get("alternative_names", []), ensure_ascii=False),
                        source_reference_id=source_reference_id,
                        observed_at=_datetime(company["observed_at"]),
                        evidence_summary=company.get("evidence_summary"),
                    )
                )
            session.flush()
            for item in plan.opportunities:
                if item.action != "create":
                    continue
                opportunity = opportunities[item.bundle_local_id]
                session.add(
                    OpportunityModel(
                        id=item.subject_id,
                        import_id=import_id,
                        bundle_local_id=item.bundle_local_id,
                        company_id=subjects["company"][opportunity["company_id"]],
                        canonical_title=opportunity["canonical_title"],
                        source_reference_id=reference_ids[opportunity["source_reference_id"]],
                        observed_at=_datetime(opportunity["observed_at"]),
                        evidence_summary=opportunity.get("evidence_summary"),
                    )
                )
                session.flush()
                for location in opportunity.get("work_locations", []):
                    session.add(
                        WorkLocationModel(
                            id=_uuid(),
                            opportunity_id=item.subject_id,
                            label=location["label"],
                            city=location.get("city"),
                            region=location.get("region"),
                            country_code=location.get("country_code"),
                            precision=location["precision"],
                            source_reference_id=reference_ids[location["source_reference_id"]],
                            observed_at=_datetime(location["observed_at"]),
                            evidence_summary=location.get("evidence_summary"),
                        )
                    )
            session.flush()
            for item in plan.postings:
                if item.action != "create":
                    continue
                posting = postings[item.bundle_local_id]
                reference = next(
                    reference for reference in bundle["source_references"] if reference["id"] == posting["source_reference_id"]
                )
                source = next(source for source in bundle["sources"] if source["id"] == reference["source_id"])
                session.add(
                    PostingModel(
                        id=item.subject_id,
                        import_id=import_id,
                        bundle_local_id=item.bundle_local_id,
                        company_id=subjects["company"][posting["company_id"]],
                        opportunity_id=subjects["opportunity"][posting["opportunity_id"]],
                        source_reference_id=reference_ids[posting["source_reference_id"]],
                        title=posting["title"],
                        external_posting_id=posting.get("external_posting_id"),
                        stable_key=posting_identity(source, reference, posting),
                        canonical_url=normalize_https_url(reference["url"]),
                        published_at=posting.get("published_at"),
                        observed_at=_datetime(posting["observed_at"]),
                        content_fingerprint=posting.get("content_fingerprint"),
                    )
                )
            session.flush()
            for item in bundle["observations"]:
                session.add(
                    ObservationModel(
                        id=_uuid(),
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        subject_type=item["subject_type"],
                        subject_id=subjects[item["subject_type"]][item["subject_id"]],
                        observation_type=item["type"],
                        value_json=json.dumps(item["value"], ensure_ascii=False),
                        source_reference_id=reference_ids[item["source_reference_id"]],
                        observed_at=_datetime(item["observed_at"]),
                        confidence=item.get("confidence"),
                        evidence_summary=item.get("evidence_summary"),
                    )
                )
            for item in bundle["assessments"]:
                session.add(
                    ExternalAssessmentModel(
                        id=_uuid(),
                        import_id=import_id,
                        bundle_local_id=item["id"],
                        subject_type=item["subject_type"],
                        subject_id=subjects[item["subject_type"]][item["subject_id"]],
                        criterion_id=item["criterion_id"],
                        value_json=json.dumps(item["value"], ensure_ascii=False),
                        origin="external_research",
                        source_reference_ids_json=json.dumps(
                            [reference_ids[reference_id] for reference_id in item["source_reference_ids"]]
                        ),
                        created_at=_datetime(item["created_at"]),
                        reasoning=item.get("reasoning"),
                    )
                )
            for item in plan.duplicate_cases:
                if item.action != "create":
                    continue
                duplicate_case = DuplicateCaseModel(
                    id=_uuid(),
                    research_import_id=import_id,
                    subject_type=item.subject_type,
                    left_subject_id=item.left_subject_id,
                    right_subject_id=item.right_subject_id,
                    evidence_summary=item.evidence_summary,
                    confidence=item.confidence,
                    created_at=datetime.now(UTC),
                )
                session.add(duplicate_case)
                session.flush()
                for reference_id in item.source_reference_ids:
                    session.add(
                        DuplicateCaseSourceReferenceModel(
                            duplicate_case_id=duplicate_case.id,
                            source_reference_id=reference_ids[reference_id],
                        )
                    )

        return ImportReport(
            import_id,
            "applied",
            bundle["bundle_id"],
            fingerprint,
            counts,
            warnings,
            bundle_version="2.0",
            prompt_context_ref=plan.prompt_context_ref,
        )

    @staticmethod
    def _report(model: ResearchImportModel) -> ImportReport:
        return ImportReport(
            import_id=model.id,
            status=model.status,
            bundle_id=model.bundle_id,
            fingerprint=model.fingerprint,
            bundle_version=model.bundle_version,
            prompt_context_ref=model.prompt_context_ref,
            counts=json.loads(model.counts_json),
            warnings=json.loads(model.warnings_json),
            issues=[ImportIssue(issue.code, issue.message, issue.path, issue.severity) for issue in model.issues],
        )
