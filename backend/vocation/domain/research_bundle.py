from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit

PROTECTED_FIELDS = {
    "tracking_status",
    "personal_assessment",
    "personal_assessments",
    "personal_decision",
    "personal_decisions",
    "exclusion",
    "exclusions",
    "group",
    "groups",
    "application_wave",
    "application_waves",
}

DUPLICATE_DECISION_OUTCOMES = (
    "confirmed_duplicate",
    "confirmed_distinct",
    "related_but_distinct",
    "keep_unresolved",
)


@dataclass(frozen=True)
class ImportIssue:
    code: str
    message: str
    path: str = "$"
    severity: str = "error"


@dataclass(frozen=True)
class ImportReport:
    import_id: str
    status: str
    bundle_id: str | None
    fingerprint: str | None
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    issues: list[ImportIssue] = field(default_factory=list)
    duplicate_of_import_id: str | None = None
    bundle_version: str | None = None
    prompt_context_ref: str | None = None
    import_kind: str = "research"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalize_https_url(value: str) -> str:
    if any(ord(character) < 32 for character in value):
        raise ValueError("URL contains control characters.")
    parsed = urlsplit(value)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("URL must be an absolute HTTPS URL.")
    if parsed.username or parsed.password:
        raise ValueError("URL user information is not allowed.")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL contains an invalid port.") from error
    hostname = parsed.hostname.encode("idna").decode("ascii").lower()
    netloc = hostname if port in (None, 443) else f"{hostname}:{port}"
    path = parsed.path or "/"
    normalized = SplitResult("https", netloc, path, parsed.query, "")
    return urlunsplit(normalized)


def find_protected_fields(value: Any, path: str = "$") -> list[ImportIssue]:
    issues: list[ImportIssue] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = f"{path}.{key}"
            if key in PROTECTED_FIELDS:
                issues.append(
                    ImportIssue(
                        code="PROTECTED_FIELD_ATTEMPT",
                        message=f"Protected Vocation field '{key}' is not allowed in a Research Bundle.",
                        path=nested_path,
                    )
                )
            issues.extend(find_protected_fields(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            issues.extend(find_protected_fields(nested, f"{path}[{index}]"))
    return issues


def source_identity(source: dict[str, Any]) -> str:
    base = source.get("base_url") or source["name"].strip().casefold()
    if source.get("base_url"):
        base = normalize_https_url(base)
    return f"{source['type']}:{base}"


def posting_identity(source: dict[str, Any], source_reference: dict[str, Any], posting: dict[str, Any]) -> str:
    if posting.get("external_posting_id"):
        return f"external:{source_identity(source)}:{posting['external_posting_id'].strip()}"
    return f"url:{normalize_https_url(source_reference['url'])}"


@dataclass(frozen=True)
class PostingIdentity:
    posting_id: str
    stable_key: str
    normalized_canonical_url: str


@dataclass(frozen=True)
class PostingIdentityInput:
    source: dict[str, Any]
    source_reference_url: str
    external_posting_id: str | None = None
    correlated_posting_id: str | None = None

    @property
    def normalized_source_reference_url(self) -> str:
        return normalize_https_url(self.source_reference_url)

    @property
    def stable_key(self) -> str | None:
        if not self.external_posting_id or not self.external_posting_id.strip():
            return None
        return posting_identity(
            self.source,
            {"url": self.source_reference_url},
            {"external_posting_id": self.external_posting_id},
        )


class PostingIdentityConflictError(ValueError):
    code = "IDENTITY_CONFLICT"

    def __init__(self, message: str):
        super().__init__(message)


@dataclass(frozen=True)
class DuplicateDecision:
    id: str
    duplicate_case_id: str
    sequence: int
    outcome: str
    reason: str
    decided_at: datetime

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("Duplicate Decision sequence must be positive.")
        if self.outcome not in DUPLICATE_DECISION_OUTCOMES:
            raise ValueError("Duplicate Decision outcome is invalid.")
        if not self.reason.strip():
            raise ValueError("Duplicate Decision reason must be nonblank.")


@dataclass(frozen=True)
class DuplicateCase:
    id: str
    research_import_id: str
    subject_type: str
    left_subject_id: str
    right_subject_id: str
    evidence_summary: str
    confidence: float | None
    source_reference_ids: tuple[str, ...]
    created_at: datetime
    decisions: tuple[DuplicateDecision, ...] = ()

    @property
    def current_decision(self) -> DuplicateDecision | None:
        return self.decisions[-1] if self.decisions else None

    @property
    def is_resolved(self) -> bool:
        current = self.current_decision
        return current is not None and current.outcome != "keep_unresolved"

    @property
    def is_reviewed(self) -> bool:
        return self.current_decision is not None


def canonical_subject_pair(subject_type: str, left_subject_id: str, right_subject_id: str) -> tuple[str, str]:
    if subject_type not in {"opportunity", "posting"}:
        raise ValueError("Duplicate Case subject type must be opportunity or posting.")
    if left_subject_id == right_subject_id:
        raise ValueError("Duplicate Case subjects must be different.")
    ordered = sorted((left_subject_id, right_subject_id))
    return ordered[0], ordered[1]
