# Vocation – v0.4.0 Release Review

**Status:** historical release closure for stable `main` v0.4.0; not the acceptance record for the current post-v0.4 `dev` product.

This checklist records why the v0.4.0 standalone baseline was accepted as a stable technical/product milestone at the time of its release. It must not be read as a claim that later post-v0.4 UI/profile/research additions are already manually product-accepted.

Current post-v0.4 release acceptance is tracked by #42 and `docs/17_MANUAL_PRODUCT_ACCEPTANCE.md`.

## Product

- [x] Domain Vision matched the released v0.4.0 purpose: externally researched job information is converted into a traceable personal job-market working set.
- [x] Core v0.4.0 workflows were present: initial/update research, validation/import, triage, availability, grouping, comparison, map, external links, applications, private documents and duplicate review.
- [x] Deliberate v0.4.0 non-goals remained outside the release instead of being partially claimed.
- [x] Vocation remained usable as a local-only application; optional WGT/Orientation integration did not take over domain authority.

## Domain language and decisions

- [x] Opportunity, Posting, Observation, Source and Source Reference were explicitly separated.
- [x] Personal Assessments and Decisions were separated from imported/external evidence.
- [x] Tracking Status, Exclusion, Availability and ApplicationCase Lifecycle had distinct semantics.
- [x] Duplicate Decisions were append-only and did not imply automatic identity merge.
- [x] ApplicationDocument content remained private and revision-bound.

## Research workflow

- [x] Initial Research Bundle 1.0 was frozen and supported.
- [x] Research Update Bundle 2.0 supported Full, Company, Opportunity and Gap Filling scopes.
- [x] Update Prompt Context Snapshots and opaque Correlation References constrained updates.
- [x] Availability Check prompting/import was separate from general Research Updates.
- [x] Imports could not overwrite protected personal state or Duplicate Decisions.

Post-v0.4 profile-aware Initial Research later added its own Vocation Prompt Context/provenance without changing Research Bundle 1.0. That later work is documented in `15_PERSONAL_SEARCH_CONTEXT.md`/`12_PROMPT_WORKFLOWS.md`, not retroactively treated as a v0.4.0 release requirement.

## Map, links and system boundaries

- [x] Work Location was the Vocation-owned spatial subject.
- [x] MapLocationResolution never silently raised Work Location precision.
- [x] Generic geocoding and rendering were delegated to Orientation through explicit boundaries.
- [x] External URLs were validated and opened only after explicit user action.
- [x] Published Opportunity Overview 1.0 and Published Map Projection 1.0 were frozen read-only contracts.

## Application workflow and private content

- [x] ApplicationCase lifecycle was explicit and independent of Opportunity Tracking Status.
- [x] ApplicationMaterial revisions remained historical.
- [x] ApplicationDocument upload, immutable revision binding, integrity validation and explicit read-only opening were implemented.
- [x] Document editing/generation/delete/retention/encryption were consciously outside the v0.4.0 baseline.

## Technical release gates

- [x] SQLite migrations were versioned and run at application startup.
- [x] Backend lint, formatting, type checks and full tests were part of repository CI.
- [x] Frontend lint, formatting, type checks, full tests, production build and OpenAPI freshness were part of repository CI.
- [x] Private/local data locations were excluded from source control.
- [x] Architecture ownership aligned with `wgt-system/architecture`.
- [x] No unresolved product issue/feature PR was required for the defined v0.4.0 standalone scope.

## Work deliberately outside v0.4.0

At the v0.4.0 release boundary, examples included:

- fuzzy/automatic identity merging/canonical-survivor rules;
- richer private document editing/generation/preview/export/retention/delete/encryption;
- additional Published capabilities without a concrete consumer;
- private cross-device transport/write synchronization;
- authentication/cloud hosting;
- Vocation-owned mobile application;
- Orientation routing without a concrete Vocation use case.

Some later product expansion has since been accepted as post-v0.4 roadmap work, notably richer personal profile/documents, structured Search Profiles, research strategies and application drafting (#46–#50). Their later acceptance does **not** mean v0.4.0 was incomplete; they are new scope.

## Historical release decision

The defined standalone Vocation scope was **accepted as complete for v0.4.0**.

The current `dev` branch is a later product state. Its automated #31 acceptance is green, but the first manual product pass on 2026-08-18 found new blockers. No next release should reuse this historical checklist as a substitute for the current #42/manual acceptance process.
