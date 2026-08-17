# Vocation – v0.4.0 Release Review

**Status:** complete standalone baseline

This checklist records the release closure of the current Vocation product scope. It is no longer a pre-implementation questionnaire.

## Product

- [x] Domain Vision matches the implemented purpose: externally researched job information is converted into a traceable personal job-market working set.
- [x] Core workflows are present: initial/update research, validation/import, triage, availability, grouping, comparison, map, external links, applications, private documents and duplicate review.
- [x] Deliberate non-goals remain outside the product instead of being partially implemented.
- [x] Vocation remains usable as a local-only application; optional WGT/Orientation integration does not take over domain authority.

## Domain language and decisions

- [x] Opportunity, Posting, Observation, Source and Source Reference are explicitly separated.
- [x] Personal Assessments and Decisions are separated from imported/external evidence.
- [x] Tracking Status, Exclusion, Availability and ApplicationCase Lifecycle have distinct semantics.
- [x] Duplicate Decisions are append-only and do not imply an automatic identity merge.
- [x] ApplicationDocument content remains private and revision-bound.

## Research workflow

- [x] Initial Research Bundle 1.0 is frozen and supported.
- [x] Research Update Bundle 2.0 supports Full, Company, Opportunity and Gap Filling scopes.
- [x] Prompt Context Snapshots and opaque Correlation References constrain updates.
- [x] Availability Check prompting/import is separate from general Research Updates.
- [x] Imports cannot overwrite protected personal state or Duplicate Decisions.

## Map, links and system boundaries

- [x] Work Location is the Vocation-owned spatial subject.
- [x] MapLocationResolution never silently raises Work Location precision.
- [x] Generic geocoding and rendering are delegated to Orientation through explicit boundaries.
- [x] External URLs are validated and opened only after explicit user action.
- [x] Published Opportunity Overview 1.0 and Published Map Projection 1.0 remain frozen read-only contracts.

## Application workflow and private content

- [x] ApplicationCase lifecycle is explicit and independent of Opportunity Tracking Status.
- [x] ApplicationMaterial revisions remain historical.
- [x] ApplicationDocument upload, immutable revision binding, integrity validation and explicit read-only opening are implemented.
- [x] Document editing/generation/delete/retention/encryption are consciously deferred rather than implied by the baseline.

## Technical release gates

- [x] SQLite migrations are versioned and run at application startup.
- [x] Backend lint, formatting, type checks and full tests are part of repository CI.
- [x] Frontend lint, formatting, type checks, full tests, production build and OpenAPI freshness are part of repository CI.
- [x] Private/local data locations are excluded from source control.
- [x] Architecture ownership is aligned with `wgt-system/architecture`.
- [x] No unresolved product issue or feature PR is required for the v0.4.0 standalone scope.

## Deferred work after v0.4.0

The following do not block this release and require their own future decision if ever needed:

- automatic/fuzzy identity merging and canonical-survivor rules;
- private document editing, generation, preview/export, retention/delete or encryption;
- additional Published Vocation capabilities without a concrete consumer;
- private cross-device transport or write synchronization;
- authentication/cloud hosting;
- Vocation-owned mobile application;
- Orientation routing without a concrete Vocation use case.

## Release decision

The current standalone Vocation scope is **accepted as complete for v0.4.0**. Further work is maintenance or separately scoped product expansion, not unfinished baseline implementation.
