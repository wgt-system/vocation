from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator, FormatChecker

from vocation.application.criteria import CriteriaService
from vocation.domain.criteria import validate_assessment_value
from vocation.domain.research_bundle import (
    ImportIssue,
    ImportReport,
    canonical_fingerprint,
    find_protected_fields,
    normalize_https_url,
    posting_identity,
)


MAX_IMPORT_BYTES = 2 * 1024 * 1024
COLLECTIONS = ("sources", "source_references", "companies", "opportunities", "postings", "observations", "assessments")


class ImportRepository(Protocol):
    def find_applied(self, fingerprint: str) -> ImportReport | None: ...
    def identity_issues(self, bundle: dict[str, Any]) -> list[ImportIssue]: ...
    def record_rejected(
        self,
        *,
        bundle_id: str | None,
        fingerprint: str | None,
        warnings: list[str],
        issues: list[ImportIssue],
    ) -> ImportReport: ...
    def apply(self, bundle: dict[str, Any], fingerprint: str) -> ImportReport: ...
    def get_report(self, import_id: str) -> ImportReport | None: ...


class ImportService:
    def __init__(self, repository: ImportRepository, criteria: CriteriaService, schema_path: Path):
        self.repository = repository
        self.criteria = criteria
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def import_text(self, content: str) -> ImportReport:
        if len(content.encode("utf-8")) > MAX_IMPORT_BYTES:
            return self.repository.record_rejected(
                bundle_id=None,
                fingerprint=None,
                warnings=[],
                issues=[ImportIssue("INPUT_TOO_LARGE", f"Bundle exceeds the {MAX_IMPORT_BYTES} byte limit.")],
            )
        try:
            bundle = json.loads(content)
        except (json.JSONDecodeError, UnicodeError) as error:
            return self.repository.record_rejected(
                bundle_id=None,
                fingerprint=None,
                warnings=[],
                issues=[ImportIssue("INVALID_JSON", str(error))],
            )
        if not isinstance(bundle, dict):
            return self.repository.record_rejected(
                bundle_id=None,
                fingerprint=None,
                warnings=[],
                issues=[ImportIssue("SCHEMA_VALIDATION_FAILED", "Top-level JSON value must be an object.")],
            )

        try:
            fingerprint = canonical_fingerprint(bundle)
        except (TypeError, ValueError) as error:
            return self.repository.record_rejected(
                bundle_id=bundle.get("bundle_id"),
                fingerprint=None,
                warnings=[],
                issues=[ImportIssue("INVALID_JSON", str(error))],
            )
        previous = self.repository.find_applied(fingerprint)
        if previous:
            return ImportReport(
                import_id=previous.import_id,
                status="duplicate",
                bundle_id=previous.bundle_id,
                fingerprint=fingerprint,
                counts=previous.counts,
                warnings=previous.warnings,
                duplicate_of_import_id=previous.import_id,
            )

        issues = find_protected_fields(bundle)
        issues.extend(self._schema_issues(bundle, protected_paths={item.path for item in issues}))
        if not issues:
            issues.extend(self._semantic_issues(bundle))
            issues.extend(self.repository.identity_issues(bundle))
        warnings = bundle.get("warnings", []) if isinstance(bundle.get("warnings"), list) else []
        if issues:
            return self.repository.record_rejected(
                bundle_id=bundle.get("bundle_id") if isinstance(bundle.get("bundle_id"), str) else None,
                fingerprint=fingerprint,
                warnings=warnings,
                issues=issues,
            )
        return self.repository.apply(bundle, fingerprint)

    def get_report(self, import_id: str) -> ImportReport | None:
        return self.repository.get_report(import_id)

    def _schema_issues(self, bundle: dict[str, Any], protected_paths: set[str]) -> list[ImportIssue]:
        issues: list[ImportIssue] = []
        errors = sorted(self.validator.iter_errors(bundle), key=lambda item: list(item.absolute_path))
        for error in errors:
            path = "$" + "".join(f"[{index}]" if isinstance(index, int) else f".{index}" for index in error.absolute_path)
            if any(protected_path.startswith(path) for protected_path in protected_paths) and error.validator == "additionalProperties":
                continue
            absolute_path = list(error.absolute_path)
            if absolute_path == ["bundle_version"]:
                code = "UNSUPPORTED_BUNDLE_VERSION"
            elif absolute_path and absolute_path[-1] in {"url", "base_url"}:
                code = "INVALID_URL"
            elif error.validator == "format" and absolute_path and absolute_path[-1] in {
                "generated_at", "as_of_date", "observed_at", "published_at", "created_at"
            }:
                code = "INVALID_DATE"
            else:
                code = "SCHEMA_VALIDATION_FAILED"
            issues.append(ImportIssue(code, error.message, path))
        return issues

    def _semantic_issues(self, bundle: dict[str, Any]) -> list[ImportIssue]:
        issues: list[ImportIssue] = []
        indexed: dict[str, dict[str, dict[str, Any]]] = {}
        for collection in COLLECTIONS:
            items: dict[str, dict[str, Any]] = {}
            for index, item in enumerate(bundle[collection]):
                item_id = item["id"]
                if item_id in items:
                    issues.append(
                        ImportIssue("DUPLICATE_BUNDLE_ID", f"Duplicate ID '{item_id}' in {collection}.", f"$.{collection}[{index}].id")
                    )
                items[item_id] = item
            indexed[collection] = items

        def require(collection: str, identifier: str, path: str) -> dict[str, Any] | None:
            target = indexed[collection].get(identifier)
            if target is None:
                issues.append(ImportIssue("UNKNOWN_REFERENCE", f"Unknown {collection} reference '{identifier}'.", path))
            return target

        for index, reference in enumerate(bundle["source_references"]):
            require("sources", reference["source_id"], f"$.source_references[{index}].source_id")
            try:
                normalize_https_url(reference["url"])
            except ValueError as error:
                issues.append(ImportIssue("INVALID_URL", str(error), f"$.source_references[{index}].url"))
        for index, company in enumerate(bundle["companies"]):
            require("source_references", company["source_reference_id"], f"$.companies[{index}].source_reference_id")
        for index, opportunity in enumerate(bundle["opportunities"]):
            require("companies", opportunity["company_id"], f"$.opportunities[{index}].company_id")
            require("source_references", opportunity["source_reference_id"], f"$.opportunities[{index}].source_reference_id")
            for location_index, location in enumerate(opportunity["work_locations"]):
                require(
                    "source_references",
                    location["source_reference_id"],
                    f"$.opportunities[{index}].work_locations[{location_index}].source_reference_id",
                )
        for index, posting in enumerate(bundle["postings"]):
            company = require("companies", posting["company_id"], f"$.postings[{index}].company_id")
            opportunity = require("opportunities", posting["opportunity_id"], f"$.postings[{index}].opportunity_id")
            require("source_references", posting["source_reference_id"], f"$.postings[{index}].source_reference_id")
            if company and opportunity and opportunity["company_id"] != posting["company_id"]:
                issues.append(
                    ImportIssue(
                        "RELATIONSHIP_MISMATCH",
                        "Posting company must match its opportunity company.",
                        f"$.postings[{index}].company_id",
                    )
                )
        subject_collections = {"company": "companies", "opportunity": "opportunities", "posting": "postings"}
        for collection_name in ("observations", "assessments"):
            for index, item in enumerate(bundle[collection_name]):
                require(
                    subject_collections[item["subject_type"]],
                    item["subject_id"],
                    f"$.{collection_name}[{index}].subject_id",
                )
                reference_ids = item.get("source_reference_ids", [item.get("source_reference_id")])
                for reference_index, reference_id in enumerate(reference_ids):
                    reference_path = (
                        f"$.{collection_name}[{index}].source_reference_ids[{reference_index}]"
                        if "source_reference_ids" in item
                        else f"$.{collection_name}[{index}].source_reference_id"
                    )
                    require(
                        "source_references",
                        reference_id,
                        reference_path,
                    )

        criteria = {criterion.criterion_id: criterion for criterion in self.criteria.list(active_only=True)}
        for index, assessment in enumerate(bundle["assessments"]):
            criterion = criteria.get(assessment["criterion_id"])
            if criterion is None:
                issues.append(
                    ImportIssue(
                        "UNKNOWN_ASSESSMENT_CRITERION",
                        f"Unknown or inactive criterion '{assessment['criterion_id']}'.",
                        f"$.assessments[{index}].criterion_id",
                    )
                )
                continue
            if criterion.applicable_subject_type != assessment["subject_type"]:
                issues.append(
                    ImportIssue(
                        "SUBJECT_TYPE_MISMATCH",
                        f"Criterion '{criterion.criterion_id}' applies to {criterion.applicable_subject_type}.",
                        f"$.assessments[{index}].subject_type",
                    )
                )
            if not validate_assessment_value(criterion, assessment["value"]):
                issues.append(
                    ImportIssue(
                        "INVALID_ASSESSMENT_VALUE",
                        f"Value is incompatible with criterion '{criterion.criterion_id}'.",
                        f"$.assessments[{index}].value",
                    )
                )

        if not issues:
            seen_identities: set[str] = set()
            for index, posting in enumerate(bundle["postings"]):
                source_reference = indexed["source_references"][posting["source_reference_id"]]
                source = indexed["sources"][source_reference["source_id"]]
                identity = posting_identity(source, source_reference, posting)
                if identity in seen_identities:
                    issues.append(
                        ImportIssue("IDENTITY_CONFLICT", "Two postings resolve to the same stable identity.", f"$.postings[{index}]")
                    )
                seen_identities.add(identity)
        return issues
