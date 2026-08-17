# ADR-0012: Vocation owns Application Cases and private application material

**Status:** Accepted
**Date:** 2026-08-13

## Decision

Vocation owns application semantics through an `ApplicationCase` aggregate linked to exactly one Opportunity. Application lifecycle is separate from `Opportunity.tracking_status`, which remains triage state. Research and Availability imports never create or mutate ApplicationCases, and Groups/Application Waves never implicitly create applications.

An ApplicationCase is created only by an explicit user action. Its V1 lifecycle is `draft`, `ready`, `submitted`, `interviewing`, `offer`, and terminal `accepted`, `rejected`, or `withdrawn`. Lifecycle changes are explicit user actions and retain historical lifecycle events. Terminal cases remain readable. There is no automatic submission or transition from email, calendar, Research Bundles, Availability, or other external sources. One Opportunity has at most one active/nonterminal ApplicationCase in V1; terminal cases remain historical.

An ApplicationCase owns private `ApplicationMaterial` metadata. Material kinds are `cv`, `cover_letter`, and `other`. Metadata consists of stable material ID, ApplicationCase ID, kind, display name, revision, and created/updated timestamps. Revisions are explicit and historical. Actual content is private; storage, filesystem layout, formats, rendering, and encryption are not decided in this slice.

## Privacy and context boundaries

Private application material is never included in Published Contracts, public examples or fixtures, logs, Research/Availability Bundles, or publication endpoints. Opportunity Overview 1.0 and Map Projection 1.0 remain unchanged. A future WGT integration requires a separate explicit private boundary; Conveyance may relay only opaque protected payloads and does not own Vocation application semantics.

## Consequences

Application state is a Vocation-owned domain concern, but persistence, API, UI, document handling, encryption, synchronization, and external submission remain outside this specification slice.
