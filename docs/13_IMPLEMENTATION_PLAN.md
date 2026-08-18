# Vocation – Implementation Plan and Current Roadmap

**Status:** stable v0.4.0 standalone baseline complete; post-v0.4 personal-search/fit/research/workspace acceptance capabilities implemented on `dev`; manual product acceptance is blocked.

## 1. Purpose

This document separates three things that older revisions mixed together:

1. **completed stable v0.4.0 slices**;
2. **implemented post-v0.4 development capabilities**;
3. **current manual-acceptance product work that is not implemented yet**.

A listed future work package is not a claim that the feature exists.

## 2. Completed stable v0.4.0 baseline

The technical slice sequence that produced stable v0.4.0 is complete.

### Slice 1 – Project foundation

Repository/build/run/test foundation, local database, migrations, health/logging.

### Slice 2 – Research Bundle 1.0 contract

Frozen initial research JSON Schema, parser/validation/fingerprint and contract examples/tests.

### Slice 3 – Core import model

Company, Opportunity, Posting, Observation, Import Record and atomic Research Bundle application.

### Slice 4 – Opportunity list/detail

Initial internal Read Models, filters and React desktop presentation.

### Slice 5 – Assessments and personal decisions

Vocation criteria, External/Personal Assessments, Tracking Status, Exclusion/Restore and history.

### Slice 6 – Prompt generation

Versioned prompt templates, Prompt Scope/Context, preview/copy/save and prompt provenance.

### Slice 7 – Research Update Bundle 2.0 and duplicate evidence

Opaque correlation refs, scoped deterministic update planning, identity protection, possible Duplicate Cases and atomic update apply.

### Slice 8 – Published Opportunity Overview 1.0

Frozen client-neutral read contract and local publication boundary outside internal React OpenAPI.

### Slice 9 – Availability/Freshness

Dedicated Availability Check contract, append-only observations, evaluator, read/API/UI integration and freshness age.

### Slice 10 – Opportunity Groups/Application Waves

Group aggregate/type, ordered membership, CRUD/reorder, list/detail filters and UI.

### Slice 11 – Map/Orientation integration

Vocation-owned WorkLocation/MapLocationResolution/MapProjection with generic place/map capability delegated to Orientation. Direct Vocation Nominatim/Leaflet ownership was removed through the accepted system architecture migration.

### Slice 12 – External Links

Derived ExternalLink values, HTTPS policy, deterministic PreferredPostingSelector and explicit OS-browser open workflow.

### Slice 13 – Opportunity comparison

Read-only 2–4 Opportunity comparison with explicit missing evidence/no ranking side effects.

### Slice 14 – Published Map Projection 1.0

Frozen client-neutral URL-free map publication contract based only on existing explicit resolutions.

### Slice 15 – ApplicationCase and private ApplicationMaterial metadata

Independent application lifecycle, append-only events/material revisions and internal API/UI.

### Slice 16 – Private ApplicationDocument content

Immutable document semantic metadata, filesystem store port/adapter, upload and integrity verification.

### Slice 17 – Private ApplicationDocument access

Exact read-only content access after integrity validation and explicit `Öffnen` UI action.

### Slice 18 – Duplicate Case resolution

Append-only explicit DuplicateDecision history with four outcomes and no merge/re-parenting engine.

`docs/14_REVIEW_CHECKLIST.md` remains the historical v0.4.0 release-scope review rather than a roadmap for the current `dev` branch.

## 3. Implemented post-v0.4 qualitative acceptance wave

The #31 acceptance candidate added the missing personal search context without changing frozen Research/Published contracts.

### #32 – Candidate Profile + Search Profiles

Implemented:

- private immutable Candidate Profile revisions;
- stable multiple Search Profiles with immutable revisions;
- exactly one default Search Profile;
- persistent search policy fields and validation;
- internal API/frontend editing.

### #33 – Explainable Opportunity Fit

Implemented:

- Search-Profile-specific evaluation policy;
- deterministic weighted fit;
- separate hard-constraint state;
- evidence completeness/missing evidence;
- criterion contribution explanations;
- list/detail integration and profile-aware sorting/filtering.

### #36 – Profile-aware quality-first Initial Research

Implemented:

- exact Search Profile snapshot/provenance;
- optional exact Candidate Profile snapshot after explicit disclosure;
- Initial Research Prompt Context and opaque internal context ref;
- quality-first prompt generation;
- linked Research Bundle 1.0 import scope validation;
- legacy/manual context-free 1.0 import compatibility.

### #38 – Opportunity workspace and private notes

Implemented:

- persistent private Opportunity note isolated from Research/Fit;
- text search;
- tracking/availability/group/profile/hard-constraint/evidence filters;
- deterministic Fit/evidence/recency/company/title sorting;
- list/map composition over the same visible Opportunity set.

### #40 – First-user navigation and deterministic E2E acceptance

Implemented:

- current primary navigation around Stellenmarkt / Profil & Suche / Recherche / Organisation;
- implementation/admin tools moved to a secondary Werkzeuge area;
- empty-market/profile/research transitions;
- successful inline Initial Research import returns to Stellenmarkt;
- realistic synthetic end-to-end acceptance across profile → prompt → import → fit → personal state → update → restart.

The automated acceptance passed, but the first manual product pass later rejected substantial presentation/workflow choices. Therefore this wave is **technically complete but not a release-quality product acceptance**.

## 4. Release-preparation work already completed

### #43 – Status/document indexing

README/docs were aligned to distinguish stable v0.4.0 `main` from post-v0.4 `dev` capability work without changing package version.

### #44 – Release ancestry reconciliation

The graph-only v0.4.0 main release commit was merged back into `dev` with a regular merge. `dev` now descends cleanly from stable main and is purely ahead.

### #42 – Current parent release acceptance

Still **open**. No next version is chosen until real product acceptance passes.

## 5. First manual product pass – 2026-08-18

The local product run exposed blockers before the real current-market workflow could be considered accepted.

Authoritative detail: `docs/17_MANUAL_PRODUCT_ACCEPTANCE.md`.

### #45 – Product UI and information architecture

Blocking presentation redesign:

- remove global `Nächster Schritt` card;
- remove decorative sidebar privacy slogan;
- redesign Stellenmarkt header/filter composition and empty state;
- consistent spacing/card/control system;
- coherent German product wording;
- likely top-level areas Stellenmarkt / Profile / Recherche / Bewerbungen;
- reconsider literal Organisation / Groups/Waves presentation.

### #46 – Persistent personal career profile and document library

Planned:

- richer durable application/personal career facts;
- dated education/experience/project data;
- reusable CV/certificates/references/evidence documents;
- reuse compatible Vocation private document infrastructure;
- future reviewable document-extraction proposals;
- no premature document-reading microservice.

### #47 – Structured Search Profile editor and Search Areas

Planned:

- typed searchable role/seniority/employment/technology/industry controls;
- custom terms where necessary;
- explicit Orientation-backed place selection;
- multiple Search Areas with optional radii;
- separate remote/relocation/nationwide semantics;
- clarify strategy/priorities instead of giant catch-all textareas.

### #48 – Maintainable search vocabularies

Planned Vocation-owned role/technology/industry catalogs with aliases, lifecycle/custom values and explicit prompt-assisted proposals. Generic place data remains Orientation-owned.

### #49 – Research strategy engine and coverage

Planned explicit repeatable research runs:

- role-first;
- company-first career-page grind;
- domain/technology grind;
- regional grind;
- freshness re-check;
- gap/coverage grind.

Also planned: Company/career-page coverage state, official-source/application-route preference and stale-result handling through existing Availability semantics.

### #50 – Application workspace and assisted drafting

Planned user-facing `Bewerbungen` flow around the existing ApplicationCase/Material/Document domain plus explicit reviewable prompt-assisted cover-letter/message/profile drafts. No automatic submission.

### #52 – Windows development launcher

Planned targeted dev-launcher health/readiness/cleanup diagnostics after a manual run exposed a `.venv` native-extension access-denied/file-lock scenario and a hidden backend process that made diagnosis difficult.

## 6. Documentation alignment (#51)

Documentation is being realigned on `docs/manual-acceptance-product-direction` so it no longer says:

- Candidate/Search Profiles or Fit are future work;
- Initial Research has no Prompt Context;
- Update Bundle 2.0/Duplicate Decision/ApplicationDocument content are still unimplemented;
- automated first-user acceptance equals real product acceptance;
- the current `Profil & Suche`/`Organisation` layout is the accepted final IA.

The docs must continue to distinguish stable/released, implemented-on-dev and planned states explicitly.

## 7. Recommended execution order after documentation merge

The issues are related but should not be implemented as one uncontrolled mega-branch.

### Phase A – product shell and editor foundations

1. **#45 UI/information architecture foundation** – define the reusable page/header/card/form/control system and remove the explicitly rejected global clutter.
2. **#47 structured Search Profile editor** – because it directly fixes the current blocker and establishes reusable select/tag/search-area controls.
3. **#48 catalogs** – add stable vocabulary data underneath #47 without hard-coding all future terms into UI components.

### Phase B – durable personal context

4. **#46 personal career profile/document library** – reuse the new interaction system and existing document storage/integrity architecture.

Document extraction itself should remain a later slice inside/after #46 unless the manual career-document workflow proves the required fields first.

### Phase C – real-market coverage

5. **#49 research strategies/coverage** – encode the successful Jobsuche lessons after Search Profiles/Search Areas/catalog semantics are stable.

This is the key work package before repeating a serious broad current-market acceptance because it addresses direct company-page discovery and stale-result recall/verification.

### Phase D – applications

6. **#50 Bewerbungen/application drafting** – compose the already implemented ApplicationCase primitives with the now richer personal profile/documents.

### Parallel maintenance

7. **#52 dev launcher** can be handled independently because it should not change product/domain semantics.

### Documentation

8. **#51** stays aligned through the above changes and closes when the repository docs reflect the accepted current state after the manual-finding branch is merged.

## 8. Release gate

Do not choose the next semantic version yet.

After blocking product work is implemented:

1. run full automated repository gates;
2. start the exact local candidate cleanly;
3. rerun `docs/16_FIRST_USER_ACCEPTANCE.md` with the real Candidate/Search Profile;
4. execute real current research using the improved strategy/source/freshness rules;
5. verify original/current posting/application routes;
6. exercise Fit/search/filter/map/comparison/application flow;
7. import update/availability results and verify protected state/provenance;
8. restart and verify persistence;
9. record remaining product defects explicitly;
10. only then choose the next version, update release metadata/changelog/status and promote the exact accepted candidate to `main`/tag.

## 9. Dependency PR policy during acceptance

Open dependency PRs that broaden major-version ranges or otherwise alter the candidate should remain separate from product acceptance unless deliberately reviewed/tested. A low-risk patch update is still a separate change, not a reason to silently mutate the accepted candidate midway through manual testing.

## 10. Architecture constraints for all future work

- no silent Research/Published contract mutation;
- no shared DB/cross-context Domain Class coupling;
- Orientation owns generic place/geospatial capability;
- Vocation owns Search Area/job-market semantics;
- Candidate Profile facts remain distinct from Search Profile policy;
- external Research/Extraction/Generation output is evidence/proposal, never hidden personal mutation;
- no automatic application submission;
- no new microservice without concrete bounded-context/runtime/security justification;
- preserve local/private operation;
- every work package gets focused tests and manual acceptance relevant to its actual product behavior.
