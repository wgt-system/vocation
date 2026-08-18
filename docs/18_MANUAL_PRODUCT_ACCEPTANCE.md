# Vocation – Manual Product Acceptance and Product Direction

**Status:** manual product acceptance started on 2026-08-18 and is **blocked**

## 1. Purpose

The automated first-user acceptance proves that Vocation's current capabilities compose correctly through the real API, application and persistence layers. It does not prove that the resulting product is pleasant, efficient or semantically clear to use.

The first real local product pass on 2026-08-18 exposed blocking UX and workflow findings. Stable `main` therefore remains v0.4.0. The post-v0.4 development state on `dev` must not receive a new release version until these findings are resolved or consciously deferred and the manual acceptance is repeated.

This document records the current product findings and accepted direction. It deliberately distinguishes implemented behavior from planned work.

## 2. Implemented baseline under review

The current `dev` state already provides:

- private revisioned Candidate Profile and multiple revisioned Search Profiles;
- per-Search-Profile evaluation policy and explainable Opportunity Fit;
- profile-aware Initial Research prompts with exact context snapshots and linked Research Bundle 1.0 import;
- Research Update Bundle 2.0, Availability/Freshness, provenance and deterministic identity/update handling;
- Opportunity search/filter/sort, comparison, map, notes, tracking and decisions;
- Opportunity Groups/Application Waves;
- ApplicationCase lifecycle, revisioned ApplicationMaterial metadata and immutable private ApplicationDocument storage/open access;
- automated first-user acceptance across persistence restart.

These capabilities remain valid technical/domain building blocks. The manual findings primarily concern how they are exposed and how the real research/application workflow should be extended.

## 3. Blocking UI findings

The current presentation is not product-accepted.

Observed problems include:

- the global `Nächster Schritt` panel duplicates normal navigation and consumes disproportionate visual space;
- the sidebar footer slogan `Lokal · privat · nachvollziehbar` is decorative product copy without useful interaction value;
- the Stellenmarkt header and analysis controls collapse into one dense horizontal strip;
- an empty Stellenmarkt still exposes filters that cannot yet do useful work;
- German and English implementation vocabulary is mixed in the same surface (`Opportunities`, `Search Profile`, `Tracking Status`, `Availability`, `Group/Wave`);
- form widths, card widths, whitespace, control density and action placement are inconsistent;
- the current Candidate/Search Profile forms expose too many structured concepts as large free-text or newline-delimited fields;
- navigation helpers and repeated buttons create redundant paths instead of a stable information architecture.

Issue #45 owns the UI/information-architecture redesign.

### Presentation direction

The likely primary product areas are:

- **Stellenmarkt** – current researched opportunities and analysis;
- **Profile** – personal profile, search profiles and evaluation policy;
- **Recherche** – explicit external-research workflows;
- **Bewerbungen** – application planning, cases, documents and generated material.

These are presentation concepts. Stable domain terms such as `Opportunity`, `SearchProfile`, `OpportunityGroup`, `ApplicationWave` and `ApplicationCase` do not need to be renamed merely because the UI uses clearer German wording.

`Organisation` and literal `Groups/Waves` are not accepted as final top-level product language. Existing Group/Wave semantics may remain useful underneath more understandable collection/application-planning workflows.

## 4. Persistent personal profile and documents

The current Candidate Profile is useful for prompt provenance but not yet sufficient as a durable career profile.

The accepted direction is to enter reusable personal/career facts once and use them across many Search Profiles and applications. Planned additions in #46 include:

- contact/personal application data;
- structured education and degree records;
- structured professional, study and project experience with dates and organizations;
- skills/technologies with familiarity and context;
- languages, projects/portfolio and links;
- reusable local CVs, certificates, references and other evidence documents.

Private documents must remain local and must not be published or inserted into research prompts implicitly.

### Document extraction boundary

A PDF/OCR reader is **not** automatically a new microservice.

The staged architecture is:

1. persist documents and edit profile facts manually;
2. introduce a replaceable document-text/extraction port when extraction is implemented;
3. let extraction propose structured facts with source/provenance and explicit user acceptance;
4. extract a generic document-understanding runtime into a separate WGT service only when a second concrete consumer or materially different runtime/security/dependency requirements justify that boundary.

Vocation remains authoritative for interpreting extracted content as Candidate Profile facts. Extraction must never silently overwrite personal data.

## 5. Structured Search Profiles

The underlying Search Profile concept remains correct, but its current editor is not accepted.

Issue #47 replaces normal newline-delimited editing with typed controls where the domain is actually categorical:

- searchable target-role selection with custom terms;
- controlled seniority selection;
- controlled employment types;
- explicit work-model and relocation preferences;
- preferred/acceptable/avoided technology selectors;
- preferred/avoided industry selectors;
- structured hard constraints where possible;
- compact tags/chips rather than large textareas.

### Search areas and radii

A target place is not just a free-text label. Search Profiles should support multiple explicit search areas with optional radii where appropriate.

Generic place search/geocoding remains an Orientation capability. Vocation owns the job-search meaning of a Search Area and its radius/preferences, while Orientation supplies generic place resolution. Remote, nationwide and relocation semantics must be modeled separately rather than encoded as fake locations.

### Qualitative strategy note

The current `Ziel & Schwerpunkt` label is too vague. Qualitative trade-offs that cannot be represented by structured criteria may remain as an optional strategy note, for example learning opportunities, compensation emphasis, collaboration preferences or product/domain interests. Concepts that can be modeled as named criteria/priorities should not be hidden inside free text.

## 6. Maintainable vocabularies

Typed selectors require vocabularies that can evolve without a Vocation release for every new role name.

Issue #48 introduces Vocation-owned reference catalogs where Vocation owns the search meaning:

- role/role-term catalog;
- technology/skill-term catalog where useful;
- industry/domain catalog;
- controlled seniority and employment-type vocabularies.

Catalogs support aliases, active/deprecated state and user-created custom values. Historical Search Profile revisions must remain stable even when the catalog later changes.

A future prompt workflow may research and **propose** new terms or aliases. External research never mutates catalogs automatically; the user explicitly accepts additions.

Geographic places are not part of these catalogs and remain Orientation-owned generic data.

## 7. Real-market research lessons

The real job-search workflow showed that a single broad role/location search has poor recall and produces too many stale or weak results.

The accepted research principles are:

- prefer the official company careers page/original posting when available;
- verify that an actual application route is still active close to import time;
- inspect whole company career pages rather than searching only literal `Junior ...` titles;
- consider normal Developer, Young Professional, Trainee and adjacent titles, then evaluate real entry suitability;
- search concrete domains/technology clusters as another discovery route;
- treat posting age as a warning/verification signal, not an automatic rejection;
- preserve stale/expired findings historically but do not present them as current actionable jobs after negative Availability evidence;
- inspect broadly but return fewer high-quality Opportunities rather than filling a numeric quota.

Issue #49 turns these lessons into explicit Research Strategies / research runs rather than keeping them in chat memory.

Planned strategy families include:

1. role-first discovery;
2. company-first career-page grind;
3. domain/technology grind;
4. regional grind;
5. freshness re-check;
6. targeted gap/coverage grind.

The existing external copy/paste research boundary remains valid. No paid LLM API or automatic crawler is required.

## 8. Company coverage

A serious company-first workflow needs to remember what has already been searched even when no Opportunity was found.

The planned coverage model in #49 should distinguish a discovery/coverage company from an evidence-backed imported Opportunity and record at least:

- company/careers page under consideration;
- last research/check time and run provenance;
- relevant current roles found / none found / inaccessible / revisit required;
- ability to generate another targeted prompt for selected or uncovered companies.

This makes repeated market expansion deliberate instead of repeatedly searching the same obvious sources.

## 9. Applications and generated material

Vocation already owns `ApplicationCase`, revisioned `ApplicationMaterial` metadata and immutable private `ApplicationDocument` content. The missing piece is a coherent user-facing application workflow.

Issue #50 defines the planned **Bewerbungen** workspace and explicit prompt-assisted drafting of application material from:

- selected Opportunity evidence;
- an exact Candidate/Profile revision;
- selected reusable CV/evidence documents or structured facts;
- optional tone/template constraints.

Initial useful generated drafts include cover letters, application e-mails/messages and tailored profile summaries. Generated output remains a draft until explicitly accepted. There is no automatic submission and no hidden disclosure of profile/document data.

## 10. Development launcher finding

The first local run also exposed a developer-experience weakness: `uv sync --locked --extra dev` hit a Windows access-denied error while replacing a SQLAlchemy native extension, consistent with a still-running Python process holding the file open.

`scripts/dev.ps1` currently hides the backend process, making backend startup failures and stale child processes harder to diagnose. Issue #52 tracks targeted launcher readiness/cleanup/observability work. It must not indiscriminately terminate unrelated Python processes.

## 11. Release gate

Issue #42 remains open. No new semantic version and no `dev` → `main` promotion occurs merely because automated tests are green.

The current blocking follow-up set is:

- #45 product UI and information architecture;
- #46 persistent personal profile and document library;
- #47 structured Search Profile editor and search areas;
- #48 maintainable search vocabularies;
- #49 research strategies, company-first coverage and freshness verification;
- #50 application workspace and assisted material generation;
- #52 development launcher observability/cleanup.

Documentation alignment itself is tracked by #51.

After the blocking product work is implemented, the manual current-market procedure in `docs/17_FIRST_USER_ACCEPTANCE.md` must be repeated against real data. Only then is the next release version chosen and the exact release candidate promoted.

## 12. Contract and ownership constraints

This product direction does not silently change frozen contracts:

- Research Bundle 1.0 remains frozen;
- Research Update Bundle 2.0 remains versioned separately;
- Availability Check Bundle 1.0 remains the source of append-only posting availability evidence;
- Published Opportunity Overview 1.0 and Published Map Projection 1.0 remain frozen;
- Vocation remains locally authoritative for job-market, Search Profile, fit, application and personal Vocation state;
- Orientation remains authoritative for generic place/geospatial capabilities;
- any future generic document-understanding service requires an explicit justified architecture boundary rather than an implementation convenience split.
