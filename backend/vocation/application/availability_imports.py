from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator, FormatChecker

from vocation.application.ports import PromptContextSnapshotRepository, UpdateSubjectRepository
from vocation.domain.availability import AvailabilityCheckResult
from vocation.domain.research_bundle import ImportIssue, ImportReport, canonical_fingerprint, canonical_json

MAX_IMPORT_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class PlannedAvailabilityObservation:
    bundle_local_id: str
    posting_correlation_ref: str
    posting_id: str
    result: AvailabilityCheckResult
    observed_at: datetime
    evidence_summary: str


@dataclass(frozen=True)
class AvailabilityImportPlan:
    prompt_context_ref: str
    observations: tuple[PlannedAvailabilityObservation, ...]


@dataclass(frozen=True)
class AvailabilityImportPlanningResult:
    plan: AvailabilityImportPlan | None
    issues: tuple[ImportIssue, ...]


class AvailabilityImportRepository(Protocol):
    def find_applied_availability(self, fingerprint: str) -> ImportReport | None: ...

    def record_rejected_availability(
        self,
        *,
        bundle_id: str | None,
        fingerprint: str | None,
        bundle_version: str | None,
        warnings: list[str],
        issues: list[ImportIssue],
    ) -> ImportReport: ...

    def apply_availability(self, bundle: dict[str, Any], plan: AvailabilityImportPlan, fingerprint: str) -> ImportReport: ...

    def get_availability_report(self, import_id: str) -> ImportReport | None: ...


def _datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


class AvailabilityImportPlanner:
    def __init__(self, snapshots: PromptContextSnapshotRepository, subjects: UpdateSubjectRepository):
        self.snapshots = snapshots
        self.subjects = subjects

    def plan(self, bundle: dict[str, Any]) -> AvailabilityImportPlanningResult:
        issues: list[ImportIssue] = []
        context_ref = bundle["prompt_context_ref"]
        snapshot = self.snapshots.get(context_ref)
        if snapshot is None:
            return AvailabilityImportPlanningResult(
                None, (ImportIssue("UNKNOWN_PROMPT_CONTEXT", "Prompt Context Snapshot was not found."),)
            )
        if snapshot.scope_type != "availability_check" or canonical_json(snapshot.scope_json) != canonical_json(bundle["research_scope"]):
            issues.append(ImportIssue("SCOPE_MISMATCH", "Availability research_scope does not exactly match the saved Prompt Context."))

        selected_refs = bundle["research_scope"]["selected_correlation_refs"]
        selected_postings: dict[str, str] = {}
        for index, correlation_ref in enumerate(selected_refs):
            subject = snapshot.subject_by_correlation(correlation_ref)
            path = f"$.research_scope.selected_correlation_refs[{index}]"
            if subject is None or subject.subject_type != "posting":
                issues.append(
                    ImportIssue("UNKNOWN_CORRELATION_REFERENCE", "Correlation reference is not a Posting in this Prompt Context.", path)
                )
                continue
            if not subject.is_target:
                issues.append(ImportIssue("SCOPE_VIOLATION", "Availability results may target only selected Posting subjects.", path))
                continue
            if self.subjects.get("posting", subject.subject_id) is None:
                issues.append(ImportIssue("UNKNOWN_CORRELATION_REFERENCE", "Mapped Posting no longer exists.", path))
                continue
            selected_postings[correlation_ref] = subject.subject_id

        seen_ids: set[str] = set()
        seen_refs: set[str] = set()
        generated_at = _datetime(bundle["generated_at"])
        planned: list[PlannedAvailabilityObservation] = []
        for index, item in enumerate(bundle["observations"]):
            path = f"$.observations[{index}]"
            if item["id"] in seen_ids:
                issues.append(ImportIssue("DUPLICATE_BUNDLE_ID", f"Duplicate observation ID '{item['id']}'.", f"{path}.id"))
            seen_ids.add(item["id"])
            correlation_ref = item["posting_correlation_ref"]
            subject = snapshot.subject_by_correlation(correlation_ref)
            if subject is None:
                issues.append(
                    ImportIssue(
                        "UNKNOWN_CORRELATION_REFERENCE",
                        "Correlation reference is not in this Prompt Context.",
                        f"{path}.posting_correlation_ref",
                    )
                )
                continue
            if subject.subject_type != "posting" or not subject.is_target:
                issues.append(
                    ImportIssue(
                        "SCOPE_VIOLATION",
                        "Availability results may target only selected Posting subjects.",
                        f"{path}.posting_correlation_ref",
                    )
                )
                continue
            posting_id = selected_postings.get(correlation_ref)
            if posting_id is None:
                issues.append(
                    ImportIssue(
                        "SCOPE_VIOLATION", "Availability result refers to an unselected Posting.", f"{path}.posting_correlation_ref"
                    )
                )
                continue
            if correlation_ref in seen_refs:
                issues.append(
                    ImportIssue(
                        "DUPLICATE_AVAILABILITY_RESULT",
                        "A Posting may have exactly one Availability result per bundle.",
                        f"{path}.posting_correlation_ref",
                    )
                )
            seen_refs.add(correlation_ref)
            observed_at = _datetime(item["observed_at"])
            if observed_at > generated_at:
                issues.append(ImportIssue("INVALID_DATE", "observed_at must not be later than generated_at.", f"{path}.observed_at"))
            planned.append(
                PlannedAvailabilityObservation(
                    bundle_local_id=item["id"],
                    posting_correlation_ref=correlation_ref,
                    posting_id=posting_id,
                    result=item["result"],
                    observed_at=observed_at,
                    evidence_summary=item["evidence_summary"],
                )
            )

        if len(seen_refs) != len(selected_postings):
            missing = [ref for ref in selected_refs if ref in selected_postings and ref not in seen_refs]
            for ref in missing:
                issues.append(ImportIssue("MISSING_AVAILABILITY_RESULT", f"No Availability result was returned for '{ref}'."))
        if issues:
            return AvailabilityImportPlanningResult(None, tuple(issues))
        return AvailabilityImportPlanningResult(AvailabilityImportPlan(context_ref, tuple(planned)), ())


class AvailabilityImportService:
    def __init__(self, repository: AvailabilityImportRepository, planner: AvailabilityImportPlanner, schema_path: Path):
        self.repository = repository
        self.planner = planner
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def import_text(self, content: str) -> ImportReport:
        if len(content.encode("utf-8")) > MAX_IMPORT_BYTES:
            return self.repository.record_rejected_availability(
                bundle_id=None,
                fingerprint=None,
                bundle_version=None,
                warnings=[],
                issues=[ImportIssue("INPUT_TOO_LARGE", "Bundle exceeds the import size limit.")],
            )
        try:
            bundle = json.loads(content)
        except (json.JSONDecodeError, UnicodeError) as error:
            return self.repository.record_rejected_availability(
                bundle_id=None, fingerprint=None, bundle_version=None, warnings=[], issues=[ImportIssue("INVALID_JSON", str(error))]
            )
        if not isinstance(bundle, dict):
            return self.repository.record_rejected_availability(
                bundle_id=None,
                fingerprint=None,
                bundle_version=None,
                warnings=[],
                issues=[ImportIssue("SCHEMA_VALIDATION_FAILED", "Top-level JSON value must be an object.")],
            )
        try:
            fingerprint = canonical_fingerprint(bundle)
        except (TypeError, ValueError) as error:
            return self.repository.record_rejected_availability(
                bundle_id=bundle.get("bundle_id"),
                fingerprint=None,
                bundle_version=None,
                warnings=[],
                issues=[ImportIssue("INVALID_JSON", str(error))],
            )
        previous = self.repository.find_applied_availability(fingerprint)
        if previous:
            return ImportReport(
                previous.import_id,
                "duplicate",
                previous.bundle_id,
                fingerprint,
                previous.counts,
                previous.warnings,
                duplicate_of_import_id=previous.import_id,
                bundle_version=previous.bundle_version,
                prompt_context_ref=previous.prompt_context_ref,
                import_kind="availability_check",
            )
        bundle_version = bundle.get("bundle_version") if bundle.get("bundle_version") == "1.0" else None
        issues = [ImportIssue(self._schema_code(error), error.message, self._path(error)) for error in self.validator.iter_errors(bundle)]
        if not issues:
            planning = self.planner.plan(bundle)
            issues.extend(planning.issues)
        warnings = bundle.get("warnings", []) if isinstance(bundle.get("warnings"), list) else []
        if issues:
            return self.repository.record_rejected_availability(
                bundle_id=bundle.get("bundle_id") if isinstance(bundle.get("bundle_id"), str) else None,
                fingerprint=fingerprint,
                bundle_version=bundle_version,
                warnings=warnings,
                issues=issues,
            )
        if planning.plan is None:
            raise RuntimeError("Availability planning returned no plan without issues.")
        return self.repository.apply_availability(bundle, planning.plan, fingerprint)

    def get_report(self, import_id: str) -> ImportReport | None:
        return self.repository.get_availability_report(import_id)

    @staticmethod
    def _path(error: Any) -> str:
        return "$" + "".join(f"[{index}]" if isinstance(index, int) else f".{index}" for index in error.absolute_path)

    @staticmethod
    def _schema_code(error: Any) -> str:
        path = list(error.absolute_path)
        if error.validator == "format" and path and path[-1] in {"generated_at", "observed_at"}:
            return "INVALID_DATE"
        return "SCHEMA_VALIDATION_FAILED"
