# Vocation – Acceptance Criteria

**Status:** automated technical acceptance is green for the implemented baseline; manual product acceptance started on 2026-08-18 and is blocked by #45–#52.

## 1. Purpose

This document describes the durable acceptance criteria behind Vocation. The executable tests in `backend/tests/` and `frontend/src/**/*.test.*` remain the implementation-level source of truth for exact edge cases.

Acceptance has two different levels:

1. **automated technical/domain acceptance** – deterministic contracts, invariants, persistence, API/frontend behavior and restart safety;
2. **manual product acceptance** – real local workflow, current external market data, usability, information architecture and actual decision/application usefulness.

A green CI run is necessary but does not by itself authorize a release after a manual product blocker has been found.

## 2. Initial Research and import

### AC-IR-01 Valid initial import

Given a valid Research Bundle 1.0, Vocation creates/reuses the permitted Companies, Opportunities, Postings, Sources/References, Observations and External Assessments atomically and stores an Import Record.

### AC-IR-02 Closed/versioned contract

Unknown properties, unsupported versions, malformed references, invalid required HTTPS URLs, invalid criterion values or protected personal fields reject the bundle before domain mutation.

### AC-IR-03 Idempotency

A previously applied canonical bundle fingerprint is not applied again.

### AC-IR-04 Deterministic Posting identity

Posting identity uses the accepted deterministic Source + external posting ID rule or normalized HTTPS-URL fallback. Similar text does not cause fuzzy merge.

### AC-IR-05 Profile-aware prompt provenance

Normal Initial Research resolves an exact Search Profile revision and optionally an explicitly included Candidate Profile revision, stores an immutable prompt-context snapshot and returns an opaque internal `prompt_context_ref` separately from Research Bundle 1.0.

### AC-IR-06 Linked Initial import scope

When the inline import supplies the Initial Research prompt-context reference, Vocation verifies the returned Research Bundle 1.0 scope against that snapshot and preserves provenance. A manual/context-free 1.0 import remains valid without prompt-context provenance.

### AC-IR-07 Quality-first prompt

The generated Initial Research prompt is self-contained, embeds the expected output contract/guidance, requests source/provenance evidence, uses the selected Search Profile and does not require the external tool to mutate private Vocation state or produce an opaque final Vocation ranking.

## 3. Research Update Bundle 2.0

### AC-UP-01 Explicit dispatch

Research Bundle 1.0 is initial-only. Research Update Bundle 2.0 is dispatched separately and requires its update Prompt Context semantics.

### AC-UP-02 Scope-local correlation

Full/Company/Opportunity/Gap workflows use only Vocation-issued opaque Correlation References from the issuing Prompt Context Snapshot. Unknown/reused-out-of-context references are blockers.

### AC-UP-03 Scope enforcement

No update may create/change Subjects outside its permitted scope. Gap Filling cannot create unrelated Companies/Opportunities/Postings or possible duplicates.

### AC-UP-04 Blockers before apply

Prompt-context, scope, protected-field, identity and duplicate-evidence blockers are found before business mutation.

### AC-UP-05 Atomic apply and personal-state preservation

An accepted update is applied atomically. Exceptions roll back. Personal Assessments, Decisions, Tracking Status, private notes, Groups/Waves and Application state remain unchanged.

### AC-UP-06 Append-only external evidence

Known subjects are safely reused. New Sources/References/Observations/Assessments are added according to contract rules instead of silently rewriting historical evidence/canonical ownership.

## 4. Availability and freshness

### AC-AV-01 Dedicated contract

Availability Check Bundle 1.0 is a separate versioned boundary and does not silently become Research Update Bundle 2.0 fields.

### AC-AV-02 Conservative result mapping

- explicit available evidence derives available;
- explicit unavailable evidence derives unavailable;
- temporarily unreachable / not found / indeterminate derive uncertain;
- no observation derives unknown.

### AC-AV-03 Opportunity aggregation

Opportunity Availability is derived from its Posting states without creating a permanent Opportunity-closed truth.

### AC-AV-04 Append-only history

Availability observations remain historical and never delete the original Research Posting/Source evidence.

### AC-AV-05 Freshness meaning

`last_checked_at`/`age_days` measure age of Availability evidence. There is no automatic stale threshold that changes Availability solely because time passed.

### AC-AV-06 Private-state isolation

Availability checks never mutate Candidate/Search Profiles, Tracking Status, Personal Assessments, Decisions, notes, Groups/Waves or ApplicationCases.

## 5. Criteria, personal assessment and decisions

### AC-PA-01 Vocation-owned criteria

External bundles may reference only known active Vocation Assessment Criteria with compatible subject/value semantics. External research cannot define arbitrary new criterion semantics in a bundle.

### AC-PA-02 Personal Assessment revisions

Create/revise operations are explicit and revisioned. Only the current revision can be revised. History remains readable.

### AC-PA-03 External/personal separation

External Assessments and Personal Assessments are visibly/semantically separate. Imports never overwrite Personal Assessment history.

### AC-PA-04 Tracking/Exclusion/Restore

Tracking transitions obey the accepted states/invariants. Exclusion requires a reason; Restore references the active Exclusion and preserves decision history.

### AC-PA-05 Restart persistence

Personal assessment/decision/tracking state survives application restart against the same database.

## 6. Candidate Profile and Search Profiles

### AC-PS-01 Candidate Profile revisions

Candidate Profile updates create immutable numbered snapshots; the newest is current and private.

### AC-PS-02 Multiple Search Profiles

Multiple stable Search Profiles may exist, each with immutable revisions. Exactly one may be default.

### AC-PS-03 Candidate/Search separation

Candidate facts do not become Search Profile policy. Search Profile role/location/technology/industry/salary/hard-constraint policy does not rewrite Candidate facts.

### AC-PS-04 Search-profile validation

Mutually exclusive technology tiers, salary bounds, result-limit constraints and evaluation-policy criterion/value rules are enforced atomically.

### AC-PS-05 No publication leakage

Candidate/Search Profile contents are absent from frozen Published Opportunity Overview/Map Projection contracts and public examples unless a separate explicit contract is designed.

### Planned manual/product criteria (#46–#48)

The current textarea-heavy editor is not product-accepted. Re-acceptance additionally requires:

- reusable durable personal/career facts and document library;
- structured role/seniority/employment/technology/industry controls with custom values;
- explicit Search Areas with optional radii and Orientation-backed place selection;
- maintainable vocabularies without historical Search Profile mutation.

## 7. Explainable Opportunity Fit

### AC-FIT-01 Determinism

The same evidence + exact Search Profile revision/policy produces the same Fit result.

### AC-FIT-02 Separate hard constraints

Hard must/must-not status is represented separately from weighted Fit and can be pass/fail/unknown according to available evidence.

### AC-FIT-03 Missing evidence

Missing evidence is explicit and contributes to Evidence Completeness rather than being silently treated as a positive match.

### AC-FIT-04 Explainability

Criterion contributions expose enough value/weight/reasoning/provenance context to explain the aggregate result.

### AC-FIT-05 Candidate provenance

Candidate Profile revision is included in Fit provenance only when Candidate facts actually contribute to the current calculation.

### AC-FIT-06 No hidden mutation

Calculating/filtering/sorting by Fit never changes Tracking Status, Decisions, Assessments, notes or Application state.

## 8. Opportunity workspace

### AC-WS-01 Search/filter/sort

Text search and implemented tracking/availability/group/hard-constraint/evidence/profile-aware filters produce deterministic visible Opportunity sets.

### AC-WS-02 Profile switch safety

Changing selected Search Profile invalidates/clears old Fit display until new profile-specific results are available; results from two profile contexts are never mixed.

### AC-WS-03 Private note isolation

Create/update/clear note persists locally, survives restart and is unaffected by Research/Update imports. Note content does not alter Fit.

### AC-WS-04 List/map consistency

MapProjection is built from the same explicit filtered Opportunity set as the workspace list.

### Manual product criteria (#45)

Current control composition is not accepted. Re-acceptance requires deliberate empty/populated states, coherent grouping/responsive layout, consistent German product wording and no global `Nächster Schritt`/decorative footer clutter.

## 9. Groups/Application Waves

### AC-GR-01 Ordered membership

Group membership is unique per Group/Opportunity and maintains explicit deterministic order.

### AC-GR-02 Isolation

Group CRUD/add/remove/reorder affects only group metadata/membership and never Research/Availability/Tracking/Decision/Application semantics.

### AC-GR-03 Application Wave model

Application Wave is an OpportunityGroup type, not a hidden automation engine and not an ApplicationCase state.

### Manual product criterion

The domain model may remain, but literal `Groups/Waves`/`Organisation` is not accepted as final main-navigation wording. #45/#50 own the application-planning presentation.

## 10. Map and Orientation boundary

### AC-MAP-01 MapLocationResolution

Explicit manual/Orientation-backed resolution creates at most one current resolution per WorkLocation; deleting/re-resolving supporting data does not alter WorkLocation evidence/precision.

### AC-MAP-02 No automatic geocoding

Map render/filter/import does not silently geocode or mutate locations.

### AC-MAP-03 Orientation ownership

Generic map rendering/clustering/hit testing/place search belong to Orientation. Vocation provides job-specific scene information/actions and interprets returned action references.

### AC-MAP-04 No hidden external navigation

Selecting/rendering a map feature never automatically opens an external posting URL.

### Planned Search-Area criterion

Search Profile place/radius selection (#47) must use the accepted Orientation generic place boundary and remain semantically separate from imported WorkLocations.

## 11. External links

### AC-LINK-01 HTTPS policy

Only accepted absolute HTTPS links with host reach the OS browser adapter.

### AC-LINK-02 Deterministic preferred link

PreferredPostingSelector uses the accepted Availability → Source type → observed time → Posting ID order.

### AC-LINK-03 Explicit user action

Opening an external posting always requires explicit user action. No import/render/filter side effect starts a browser.

### AC-LINK-04 Current actionability is separate

A structurally valid URL is not proof that a Posting is still available. Availability/Freshness evidence remains the current-actionability boundary.

## 12. Opportunity comparison

### AC-CMP-01 Selection constraints

Only 2–4 unique existing Opportunities are compared in the explicit requested order.

### AC-CMP-02 Evidence semantics

Supported research/assessment dimensions show missing/multiple evidence explicitly without invented winner/contradiction semantics.

### AC-CMP-03 Read-only

Comparison never changes any Vocation state and exposes no automatic URL action.

## 13. Duplicate review

### AC-DUP-01 Possible duplicate ≠ merge

Research evidence may create/reuse a Duplicate Case but never a destructive merge.

### AC-DUP-02 Explicit append-only decision

User decisions are append-only with one of `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct`, `keep_unresolved` and a nonblank reason.

### AC-DUP-03 No re-parenting

`confirmed_duplicate` remains classification only. Opportunity/Posting identity, Assessments, Decisions, Groups, ApplicationCases/Documents and Published refs are not automatically rewritten.

## 14. ApplicationCase and private ApplicationDocuments

### AC-APP-01 Lifecycle

ApplicationCase creation/lifecycle changes are explicit, independently persisted and do not implicitly follow Opportunity Tracking Status.

### AC-APP-02 One active case invariant

At most one nonterminal active ApplicationCase exists per Opportunity; terminal history remains readable.

### AC-APP-03 Material revisions

ApplicationMaterial revisions are explicit/historical; content replacement creates a new revision rather than modifying an existing document payload in place.

### AC-APP-04 Private document integrity

Attach stores allowed payload bytes through `ApplicationDocumentStore`, verifies read-back size/SHA-256 before acceptance and persists private metadata/opaque reference only after success.

### AC-APP-05 Exact read

Opening content resolves the exact `document_id`/material revision and revalidates integrity. No implicit latest-revision fallback.

### AC-APP-06 Privacy/publication isolation

ApplicationCases/Materials/Documents are absent from frozen public Published contracts and from Research imports.

### Planned product criteria (#46/#50)

Re-acceptance of the broader application product requires reusable profile documents, coherent `Bewerbungen` workspace and explicitly reviewed application-material generation without automatic submission/hidden disclosure.

## 15. Published contracts

### AC-PUB-01 Opportunity Overview 1.0

Validates exactly against `schemas/published-opportunity-overview-v1.schema.json`, uses opaque refs and contains only frozen fields.

### AC-PUB-02 Published Map Projection 1.0

Validates exactly against `schemas/published-map-projection-v1.schema.json`, is URL-free and publishes only existing explicit resolutions without geocoding/mutation.

### AC-PUB-03 No silent expansion

Internal post-v0.4 Candidate/Search/Fit/workspace/application changes do not silently add fields to frozen contracts.

### AC-PUB-04 Publication age

Publication generated time/age must not be interpreted as Posting Availability/Freshness.

## 16. First-user end-to-end automated acceptance

The deterministic fixture `examples/acceptance/first-user-market.json` and `backend/tests/test_first_user_acceptance.py` exercise the real application/API/persistence path:

1. Candidate Profile;
2. default Search Profile + evaluation policy;
3. exact Initial Research prompt context;
4. linked Research Bundle 1.0 import;
5. explainable Fit;
6. personal note/tracking/decision/group state;
7. correlation-ref Update 2.0;
8. protected-state/provenance preservation;
9. application restart and state verification.

Frontend acceptance verifies the corresponding navigation/transitions including successful inline research import returning to Stellenmarkt.

This automated path is green but does not override the manual UX findings.

## 17. Manual current-market/product acceptance

The first manual product pass on 2026-08-18 stopped before real current-market completion because the current empty-market/Profile UI already failed product acceptance.

Blocking areas:

- #45 product UI/information architecture;
- #46 persistent personal profile/documents;
- #47 structured Search Profile/Search Areas;
- #48 maintainable vocabularies;
- #49 research strategy/company-first/freshness coverage;
- #50 application workspace/drafting;
- #52 dev launcher startup/cleanup observability.

After resolution, `docs/18_FIRST_USER_ACCEPTANCE.md` must be rerun with real current postings and official source/application-route verification.

## 18. Research-strategy acceptance direction (#49)

Future explicit research runs must satisfy:

- company-first/role-first/domain/regional/freshness/gap strategies are intentional and traceable;
- official company/original sources are preferred when available;
- an active application route is verified close to import time where practical;
- broad inspection does not force quota-filling weak Opportunities;
- stale/expired evidence stays historical but is no longer presented as actionable after negative Availability evidence;
- Company coverage can remember `checked/no relevant role` without fabricating an Opportunity.

## 19. Development/runtime acceptance (#52)

The normal Windows dev launcher must eventually make backend failure/readiness visible and clean up its exact child process so a normal stop does not leave a stale Vocation process locking `.venv` native extensions.

It must never indiscriminately kill unrelated Python processes.

## 20. Release rule

A next release is eligible only when:

- required automated repository gates pass on the exact candidate;
- manual product blockers are resolved or explicitly accepted/deferred;
- current-market acceptance is rerun successfully;
- version/status/changelog metadata are intentionally aligned;
- `dev` is promoted through the documented release model without silent contract changes.
