from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
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
