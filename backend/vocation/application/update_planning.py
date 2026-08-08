from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from vocation.application.criteria import CriteriaService
from vocation.application.duplicate_cases import DuplicateCaseRepository
from vocation.application.ports import PromptContextSnapshotRepository, UpdateSubjectRepository
from vocation.application.posting_identity import PostingIdentityResolver
from vocation.domain.criteria import validate_assessment_value
from vocation.domain.research_bundle import (
    ImportIssue,
    PostingIdentityInput,
    canonical_json,
    canonical_subject_pair,
    normalize_https_url,
)
from vocation.domain.update_import import (
    PlannedDuplicateCase,
    PlannedSubject,
    PromptContextSnapshot,
    PromptContextSubject,
    SubjectType,
    UpdateImportPlan,
)


@dataclass(frozen=True)
class UpdateImportPlanningResult:
    plan: UpdateImportPlan | None
    issues: tuple[ImportIssue, ...]


class UpdateImportPlanner:
    def __init__(
        self,
        snapshots: PromptContextSnapshotRepository,
        subjects: UpdateSubjectRepository,
        criteria: CriteriaService,
        posting_identity: PostingIdentityResolver,
        duplicate_cases: DuplicateCaseRepository,
        id_factory: Callable[[], str] = lambda: str(uuid4()),
    ):
        self.snapshots = snapshots
        self.subjects = subjects
        self.criteria = criteria
        self.posting_identity = posting_identity
        self.duplicate_cases = duplicate_cases
        self.id_factory = id_factory

    def plan(self, bundle: dict) -> UpdateImportPlanningResult:
        issues: list[ImportIssue] = []
        snapshot = self.snapshots.get(bundle.get("prompt_context_ref", ""))
        if snapshot is None:
            return UpdateImportPlanningResult(None, (ImportIssue("UNKNOWN_PROMPT_CONTEXT", "Prompt Context Snapshot was not found."),))
        scope = bundle.get("research_scope", {})
        if canonical_json(scope) != canonical_json(snapshot.scope_json):
            issues.append(ImportIssue("SCOPE_MISMATCH", "Research scope does not exactly match the Prompt Context Snapshot."))
        indexes = self._indexes(bundle, issues)
        if issues:
            return UpdateImportPlanningResult(None, tuple(issues))
        mappings = {subject.correlation_ref: subject for subject in snapshot.subjects}
        resolved: dict[tuple[SubjectType, str], PromptContextSubject] = {}
        for subject_type in ("company", "opportunity", "posting"):
            for item in indexes[subject_type].values():
                correlation_ref = item.get("correlation_ref")
                if not correlation_ref:
                    continue
                mapping = mappings.get(correlation_ref)
                if mapping is None or mapping.subject_type != subject_type:
                    issues.append(
                        ImportIssue(
                            "UNKNOWN_CORRELATION_REFERENCE",
                            f"Unknown or incorrectly typed correlation reference '{correlation_ref}'.",
                        )
                    )
                    continue
                if not self._subject_exists(mapping):
                    issues.append(
                        ImportIssue(
                            "UNKNOWN_CORRELATION_REFERENCE",
                            f"Correlation reference '{correlation_ref}' points to a missing subject.",
                        )
                    )
                    continue
                key = (subject_type, mapping.subject_id)
                if key in resolved:
                    issues.append(ImportIssue("IDENTITY_CONFLICT", "Multiple bundle subjects resolve to one existing subject."))
                resolved[key] = mapping
        if issues:
            return UpdateImportPlanningResult(None, tuple(issues))

        companies = self._plan_companies(indexes["company"], resolved, snapshot, scope["type"], issues)
        company_by_bundle = {item.bundle_local_id: item for item in companies}
        opportunities = self._plan_opportunities(indexes["opportunity"], company_by_bundle, resolved, snapshot, scope["type"], issues)
        opportunity_by_bundle = {item.bundle_local_id: item for item in opportunities}
        postings = self._plan_postings(
            indexes["posting"],
            company_by_bundle,
            opportunity_by_bundle,
            resolved,
            snapshot,
            scope["type"],
            indexes,
            issues,
        )
        posting_by_bundle = {item.bundle_local_id: item for item in postings}
        self._validate_evidence_targets(bundle, indexes, company_by_bundle, opportunity_by_bundle, posting_by_bundle, scope, issues)
        self._validate_gap_requests(bundle, indexes, resolved, scope, issues)
        self._validate_assessments(bundle, indexes, issues)
        duplicates = self._plan_duplicates(bundle, indexes, company_by_bundle, opportunity_by_bundle, posting_by_bundle, issues)
        if issues:
            return UpdateImportPlanningResult(None, tuple(issues))
        return UpdateImportPlanningResult(
            UpdateImportPlan(
                prompt_context_ref=snapshot.prompt_context_ref,
                scope_type=snapshot.scope_type,
                companies=tuple(companies),
                opportunities=tuple(opportunities),
                postings=tuple(postings),
                duplicate_cases=tuple(duplicates),
            ),
            (),
        )

    def _indexes(self, bundle: dict, issues: list[ImportIssue]) -> dict[str, dict[str, dict]]:
        collections = ("sources", "source_references", "companies", "opportunities", "postings", "observations", "assessments")
        indexes: dict[str, dict[str, dict]] = {}
        for collection in collections:
            items = {}
            for index, item in enumerate(bundle.get(collection, [])):
                identifier = item.get("id")
                if identifier in items:
                    issues.append(ImportIssue("DUPLICATE_BUNDLE_ID", f"Duplicate ID '{identifier}'.", f"$.{collection}[{index}].id"))
                items[identifier] = item
            indexes[collection] = items
        indexes["company"] = indexes["companies"]
        indexes["opportunity"] = indexes["opportunities"]
        indexes["posting"] = indexes["postings"]
        indexes["possible_duplicates"] = {item.get("id"): item for item in bundle.get("possible_duplicates", [])}

        def require(collection: str, identifier: str, path: str) -> dict | None:
            value = indexes[collection].get(identifier)
            if value is None:
                issues.append(ImportIssue("UNKNOWN_REFERENCE", f"Unknown {collection} reference '{identifier}'.", path))
            return value

        for index, item in enumerate(bundle.get("source_references", [])):
            require("sources", item.get("source_id"), f"$.source_references[{index}].source_id")
            try:
                normalize_https_url(item["url"])
            except (KeyError, ValueError) as error:
                issues.append(ImportIssue("INVALID_URL", str(error), f"$.source_references[{index}].url"))
        for index, item in enumerate(bundle.get("companies", [])):
            if item.get("source_reference_id"):
                require("source_references", item["source_reference_id"], f"$.companies[{index}].source_reference_id")
        for index, item in enumerate(bundle.get("opportunities", [])):
            require("companies", item.get("company_id"), f"$.opportunities[{index}].company_id")
            if item.get("source_reference_id"):
                require("source_references", item["source_reference_id"], f"$.opportunities[{index}].source_reference_id")
            for location_index, location in enumerate(item.get("work_locations", [])):
                require(
                    "source_references",
                    location.get("source_reference_id"),
                    f"$.opportunities[{index}].work_locations[{location_index}].source_reference_id",
                )
        for index, item in enumerate(bundle.get("postings", [])):
            company = require("companies", item.get("company_id"), f"$.postings[{index}].company_id")
            opportunity = require("opportunities", item.get("opportunity_id"), f"$.postings[{index}].opportunity_id")
            if item.get("source_reference_id"):
                require("source_references", item["source_reference_id"], f"$.postings[{index}].source_reference_id")
            evidence = item.get("identity_evidence")
            if evidence:
                require(
                    "source_references", evidence.get("source_reference_id"), f"$.postings[{index}].identity_evidence.source_reference_id"
                )
            if company and opportunity and company.get("id") != opportunity.get("company_id"):
                issues.append(ImportIssue("RELATIONSHIP_MISMATCH", "Posting company must match its opportunity company."))
        subjects = {"company": "companies", "opportunity": "opportunities", "posting": "postings"}
        for collection in ("observations", "assessments"):
            for index, item in enumerate(bundle.get(collection, [])):
                require(subjects[item.get("subject_type")], item.get("subject_id"), f"$.{collection}[{index}].subject_id")
                reference_ids = item.get("source_reference_ids", [item.get("source_reference_id")])
                for reference_index, reference_id in enumerate(reference_ids):
                    require("source_references", reference_id, f"$.{collection}[{index}].source_reference_ids[{reference_index}]")
        for index, item in enumerate(bundle.get("possible_duplicates", [])):
            if item.get("subject_type") not in {"opportunity", "posting"}:
                issues.append(ImportIssue("INVALID_DUPLICATE_EVIDENCE", "Duplicate evidence subject type is invalid."))
                continue
            collection = subjects[item["subject_type"]]
            require(collection, item.get("left_subject_id"), f"$.possible_duplicates[{index}].left_subject_id")
            require(collection, item.get("right_subject_id"), f"$.possible_duplicates[{index}].right_subject_id")
            for reference_id in item.get("source_reference_ids", []):
                require("source_references", reference_id, f"$.possible_duplicates[{index}].source_reference_ids")
        return indexes

    def _subject_exists(self, mapping: PromptContextSubject) -> bool:
        return self.subjects.get(mapping.subject_type, mapping.subject_id) is not None

    def _plan_companies(
        self, items: dict[str, dict], resolved: dict, snapshot: PromptContextSnapshot, scope_type: str, issues: list[ImportIssue]
    ) -> list[PlannedSubject]:
        planned: list[PlannedSubject] = []
        for bundle_id, item in items.items():
            if item.get("correlation_ref"):
                mapping = next((value for value in resolved.values() if value.correlation_ref == item["correlation_ref"]), None)
                assert mapping is not None
                planned.append(PlannedSubject(bundle_id, "company", mapping.subject_id, "reuse", mapping.is_target))
            else:
                if scope_type != "full_update":
                    issues.append(ImportIssue("SCOPE_VIOLATION", "This update scope cannot create a Company."))
                    continue
                planned.append(PlannedSubject(bundle_id, "company", self.id_factory(), "create", True))
        return planned

    def _plan_opportunities(
        self,
        items: dict[str, dict],
        companies: dict[str, PlannedSubject],
        resolved: dict,
        snapshot: PromptContextSnapshot,
        scope_type: str,
        issues: list[ImportIssue],
    ) -> list[PlannedSubject]:
        planned: list[PlannedSubject] = []
        for bundle_id, item in items.items():
            company = companies.get(self._value(item, "company_id"))
            if company is None:
                continue
            if item.get("correlation_ref"):
                mapping = next(value for value in resolved.values() if value.correlation_ref == item["correlation_ref"])
                existing = self.subjects.get("opportunity", mapping.subject_id)
                if existing and existing.company_id != company.subject_id:
                    issues.append(ImportIssue("SCOPE_VIOLATION", "Known Opportunity ownership does not match its Company."))
                planned.append(PlannedSubject(bundle_id, "opportunity", mapping.subject_id, "reuse", mapping.is_target))
            else:
                if scope_type in {"opportunity_update", "gap_filling"}:
                    issues.append(ImportIssue("SCOPE_VIOLATION", "This update scope cannot create an Opportunity."))
                    continue
                if scope_type == "company_update" and not company.is_target:
                    issues.append(ImportIssue("SCOPE_VIOLATION", "New Opportunity must belong to a target Company."))
                    continue
                planned.append(PlannedSubject(bundle_id, "opportunity", self.id_factory(), "create", True))
        return planned

    def _plan_postings(
        self,
        items: dict[str, dict],
        companies: dict[str, PlannedSubject],
        opportunities: dict[str, PlannedSubject],
        resolved: dict,
        snapshot: PromptContextSnapshot,
        scope_type: str,
        indexes: dict,
        issues: list[ImportIssue],
    ) -> list[PlannedSubject]:
        planned: list[PlannedSubject] = []
        resolved_existing: set[str] = set()
        for bundle_id, item in items.items():
            company = companies.get(self._value(item, "company_id"))
            opportunity = opportunities.get(self._value(item, "opportunity_id"))
            if company is None or opportunity is None:
                continue
            correlation_ref = item.get("correlation_ref")
            if correlation_ref:
                mapping = next(value for value in resolved.values() if value.correlation_ref == correlation_ref)
                posting_id = mapping.subject_id
                evidence = item.get("identity_evidence")
                if evidence:
                    reference: dict | None = indexes["source_references"].get(evidence["source_reference_id"])
                    if reference is None:
                        continue
                    source: dict | None = indexes["sources"].get(reference["source_id"])
                    if source is None:
                        continue
                    try:
                        resolution = self.posting_identity.resolve(
                            PostingIdentityInput(source, reference["url"], evidence.get("external_posting_id"), posting_id)
                        )
                        if not resolution.posting or resolution.posting.posting_id != posting_id:
                            raise ValueError("Identity evidence does not match the correlated Posting.")
                    except ValueError as error:
                        issues.append(ImportIssue("IDENTITY_CONFLICT", str(error)))
                existing = self.subjects.get("posting", posting_id)
                if existing and (existing.company_id != company.subject_id or existing.opportunity_id != opportunity.subject_id):
                    issues.append(ImportIssue("IDENTITY_CONFLICT", "Known Posting ownership does not match its relationships."))
                if posting_id in resolved_existing:
                    issues.append(ImportIssue("IDENTITY_CONFLICT", "Multiple bundle Postings resolve to one existing Posting."))
                resolved_existing.add(posting_id)
                planned.append(PlannedSubject(bundle_id, "posting", posting_id, "reuse", mapping.is_target))
                continue
            posting_reference: dict | None = indexes["source_references"].get(self._value(item, "source_reference_id"))
            if posting_reference is None:
                continue
            posting_source: dict | None = indexes["sources"].get(posting_reference["source_id"])
            if posting_source is None:
                continue
            try:
                resolution = self.posting_identity.resolve(
                    PostingIdentityInput(posting_source, posting_reference["url"], item.get("external_posting_id"))
                )
            except ValueError as error:
                issues.append(ImportIssue("IDENTITY_CONFLICT", str(error)))
                continue
            if resolution.posting:
                mapping = next(
                    (
                        value
                        for value in snapshot.subjects
                        if value.subject_type == "posting" and value.subject_id == resolution.posting.posting_id
                    ),
                    None,
                )
                if mapping is None or not mapping.is_target:
                    issues.append(ImportIssue("SCOPE_VIOLATION", "Deterministic Posting resolution is outside the current target scope."))
                    continue
                existing = self.subjects.get("posting", resolution.posting.posting_id)
                if existing and (existing.company_id != company.subject_id or existing.opportunity_id != opportunity.subject_id):
                    issues.append(ImportIssue("IDENTITY_CONFLICT", "Reused Posting ownership does not match its relationships."))
                if resolution.posting.posting_id in resolved_existing:
                    issues.append(ImportIssue("IDENTITY_CONFLICT", "Multiple bundle Postings resolve to one existing Posting."))
                resolved_existing.add(resolution.posting.posting_id)
                planned.append(PlannedSubject(bundle_id, "posting", resolution.posting.posting_id, "reuse", True))
            else:
                if (
                    scope_type == "gap_filling"
                    or (scope_type == "company_update" and not opportunity.is_target)
                    or (scope_type == "opportunity_update" and not opportunity.is_target)
                ):
                    issues.append(ImportIssue("SCOPE_VIOLATION", "New Posting is outside the permitted update scope."))
                    continue
                planned.append(PlannedSubject(bundle_id, "posting", self.id_factory(), "create", True))
        return planned

    def _validate_evidence_targets(
        self, bundle: dict, indexes: dict, companies: dict, opportunities: dict, postings: dict, scope: dict, issues: list[ImportIssue]
    ) -> None:
        for collection in ("observations", "assessments"):
            for item in bundle.get(collection, []):
                planned = {"company": companies, "opportunity": opportunities, "posting": postings}[item["subject_type"]].get(
                    item["subject_id"]
                )
                if planned and not planned.is_target:
                    issues.append(ImportIssue("SCOPE_VIOLATION", "Evidence cannot target a context-only subject."))

    def _validate_gap_requests(self, bundle: dict, indexes: dict, resolved: dict, scope: dict, issues: list[ImportIssue]) -> None:
        if scope["type"] != "gap_filling":
            return
        requests = scope.get("requests", [])
        for item in bundle.get("observations", []):
            correlation = indexes[{"company": "companies", "opportunity": "opportunities", "posting": "postings"}[item["subject_type"]]][
                item["subject_id"]
            ].get("correlation_ref")
            if not any(
                request.get("subject_type") == item["subject_type"]
                and request.get("correlation_ref") == correlation
                and request.get("observation_type") == item["type"]
                for request in requests
            ):
                issues.append(ImportIssue("SCOPE_VIOLATION", "Gap Filling returned an unrequested Observation."))
        for item in bundle.get("assessments", []):
            correlation = indexes[{"company": "companies", "opportunity": "opportunities", "posting": "postings"}[item["subject_type"]]][
                item["subject_id"]
            ].get("correlation_ref")
            if not any(
                request.get("subject_type") == item["subject_type"]
                and request.get("correlation_ref") == correlation
                and request.get("criterion_id") == item["criterion_id"]
                for request in requests
            ):
                issues.append(ImportIssue("SCOPE_VIOLATION", "Gap Filling returned an unrequested Assessment."))

    def _validate_assessments(self, bundle: dict, indexes: dict, issues: list[ImportIssue]) -> None:
        criteria = {criterion.criterion_id: criterion for criterion in self.criteria.list(active_only=True)}
        for item in bundle.get("assessments", []):
            criterion = criteria.get(item["criterion_id"])
            if criterion is None:
                issues.append(ImportIssue("UNKNOWN_ASSESSMENT_CRITERION", f"Unknown or inactive criterion '{item['criterion_id']}'."))
            elif criterion.applicable_subject_type != item["subject_type"]:
                issues.append(ImportIssue("SUBJECT_TYPE_MISMATCH", "Assessment criterion subject type does not match."))
            elif not validate_assessment_value(criterion, item["value"]):
                issues.append(ImportIssue("INVALID_ASSESSMENT_VALUE", "Assessment value is invalid for the criterion."))

    def _plan_duplicates(
        self, bundle: dict, indexes: dict, companies: dict, opportunities: dict, postings: dict, issues: list[ImportIssue]
    ) -> list[PlannedDuplicateCase]:
        planned: list[PlannedDuplicateCase] = []
        for item in bundle.get("possible_duplicates", []):
            subjects = opportunities if item["subject_type"] == "opportunity" else postings
            left = subjects.get(item["left_subject_id"])
            right = subjects.get(item["right_subject_id"])
            if left is None or right is None:
                continue
            if left.subject_id == right.subject_id:
                issues.append(ImportIssue("INVALID_DUPLICATE_EVIDENCE", "Duplicate evidence resolves to the same subject."))
                continue
            if not left.is_target or not right.is_target:
                issues.append(ImportIssue("SCOPE_VIOLATION", "Duplicate evidence cannot include a context-only subject."))
                continue
            left_id, right_id = canonical_subject_pair(item["subject_type"], left.subject_id, right.subject_id)
            existing = self.duplicate_cases.find_by_pair(item["subject_type"], left_id, right_id)
            planned.append(
                PlannedDuplicateCase(
                    bundle_local_id=item["id"],
                    subject_type=item["subject_type"],
                    left_subject_id=left_id,
                    right_subject_id=right_id,
                    action="reuse" if existing else "create",
                    evidence_summary=item["evidence_summary"].strip(),
                    confidence=item.get("confidence"),
                    source_reference_ids=tuple(item["source_reference_ids"]),
                )
            )
        return planned

    @staticmethod
    def _value(item: dict, key: str) -> str:
        return str(item[key])
