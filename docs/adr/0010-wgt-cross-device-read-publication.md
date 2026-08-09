# ADR-0010: WGT Cross-device Read Publication

- Status: Accepted
- Date: 2026-08-09

## Context

Vocation is an independent, local-first Job-Market bounded context and remains the local authority for Opportunities, Postings, personal state, and research semantics. Its existing `/api/...` React API is an internal presentation API, not automatically a published cross-context contract. Wiiii Got This is the primary cross-device presentation for suitable everyday Vocation capabilities on Windows and iPhone.

## Decision

Vocation publishes versioned, client-neutral read projections through a Vocation-specific Publication Adapter. The first concrete integration candidate is the small read-only `Opportunity Overview` Published Capability 1.0; its final field schema is defined by a later contract-test slice.

The publication path is:

```text
Vocation local authority
  → Vocation Publication Adapter
  → optional generic Relay/Storage
  → Wiiii Got This
  → Windows / iPhone
```

WGT never reads the Vocation database, imports Vocation domain classes, or owns Vocation business semantics. The same Published Contract may be consumed by WGT Windows and WGT iPhone. A future relay can be added without changing the Published Contract. Relay/Storage is transport, storage, authentication, and envelope infrastructure only; it is not a Sync bounded context and performs no identity, merge, assessment, decision, or conflict semantics.

Publication is optional. Full local-only Vocation operation remains supported. A Published Projection is derived and rebuildable, never a second domain authority. Publication Snapshot age is distinct from domain Freshness and must not imply that a Posting is stale or unavailable. Different data classes may later receive different publication, encryption, or local-only policies; this ADR does not freeze privacy policy.

Read publication is preferred over embedding Python/FastAPI in the iPhone WGT client or requiring the Windows PC to remain on. The iPhone can use the last published projection while the PC is off. Cross-device writes remain undecided; any future write capability requires Vocation-owned command and conflict semantics plus a new architecture decision.

ADR-0007 remains accepted and is not superseded. No separate Sync bounded context is introduced at this stage.

## Consequences

- Vocation remains standalone and independently runnable.
- Data Publication is a Vocation-owned supporting subdomain/application responsibility.
- The first post-v0.3 vertical slice is a transport-independent Opportunity Overview 1.0 projection and contract tests.
- No iOS implementation or remote relay implementation is part of that slice.
- No personal-state write commands are published by this decision.
