# ADR-0010: WGT Cross-device Read Publication

- Status: Accepted
- Date: 2026-08-09

## Context

Vocation is an independent, local-first Job-Market bounded context and remains the local authority for Opportunities, Postings, personal state, and research semantics. Its existing `/api/...` React API is an internal presentation API, not automatically a published cross-context contract. Wiiii Got This owns cross-device/client integration and presentation for suitable Vocation capabilities on Windows and iPhone. Conveyance is a separate generic Synchronization/Relay bounded context.

## Decision

Vocation publishes versioned, client-neutral read projections through a Vocation-specific Publication Adapter. The first concrete integration candidate is the read-only `Opportunity Overview` Published Capability 1.0, whose canonical schema and contract tests remain Vocation-owned. The Published Contract is transport-independent and is the source of contract truth.

The publication path is:

```text
Vocation local authority
  → Vocation Publication Adapter
  → Wiiii Got This Windows
  → Conveyance (opaque protected delivery)
  → Wiiii Got This iPhone
```

Vocation does not integrate with Conveyance directly. WGT Windows consumes the Vocation Published Contract, protects the complete payload, and publishes the resulting opaque envelope to Conveyance. WGT iPhone later retrieves the opaque envelope from Conveyance, verifies and decrypts it locally, and validates the original Vocation Published Contract. WGT never reads the Vocation database, imports Vocation domain classes, or owns Vocation business semantics. Conveyance owns generic durable delivery and technical delivery/trust mechanisms only; it performs no Vocation identity, merge, assessment, decision, or conflict semantics and cannot interpret Vocation payloads.

Publication is optional. Full local-only Vocation operation remains supported. A Published Projection is derived and rebuildable, never a second domain authority. Publication Snapshot age is distinct from domain Freshness and must not imply that a Posting is stale or unavailable. Different data classes may later receive different publication, encryption, or local-only policies; this ADR does not freeze privacy policy.

Read publication is preferred over embedding Python/FastAPI in the iPhone WGT client or requiring the Windows PC to remain on. The iPhone can use the last published projection while the PC is off. Cross-device writes remain undecided; any future write capability requires Vocation-owned command and conflict semantics plus a new architecture decision.

ADR-0007 remains accepted and is not superseded. Conveyance is the separately accepted generic Synchronization/Relay bounded context; its security and trust mechanisms do not transfer Vocation business ownership or contract authority.

## Consequences

- Vocation remains standalone and independently runnable.
- Data Publication is a Vocation-owned supporting subdomain/application responsibility.
- The first post-v0.3 vertical slice is a transport-independent Opportunity Overview 1.0 projection and contract tests.
- WGT owns the Windows/iPhone integration and presentation path; Conveyance owns only opaque protected delivery.
- No Vocation-to-Conveyance direct integration or remote relay implementation is part of the Vocation slice.
- No personal-state write commands are published by this decision.
