# Vocation – Read Models

**Status:** current through the implemented post-v0.4 Opportunity workspace, Candidate/Search Profile, explainable Fit and first-user acceptance baseline. Planned product views are marked.

## 1. Principle

Read Models are purpose-specific projections. They own no business truth and may not create contradictory copies of domain state.

A Presentation rename does not require a Read Model/domain rename. Internal `Opportunity`, `SearchProfile`, `OpportunityGroup` etc. may be rendered with clearer German product language.

## 2. Opportunity workspace/list item

The current Opportunity workspace composes list data with Vocation-owned local analysis state.

Typical fields include:

- Opportunity ID;
- title and Company;
- known Work Location labels/precision;
- Tracking Status;
- Availability and availability-evidence Freshness;
- Group/Wave memberships;
- valid/preferred posting-link availability;
- Search-Profile-aware Fit summary when a profile is selected;
- evidence completeness;
- hard-constraint state;
- imported/recency metadata used by supported sort modes.

Workspace controls currently support:

- free-text search across title/company/location;
- Tracking Status;
- Availability;
- Group/Wave;
- selected/default Search Profile;
- hard-constraint result;
- missing-evidence state;
- deterministic sorting by Fit/evidence/recency/company/title;
- list/map mode.

Searching/filtering/sorting never mutates Opportunity, Decision, Assessment, Group or Application state.

### Manual-acceptance finding

The current read capability is valid, but its UI presentation is not accepted. The first manual pass found that title/count/search/profile/status/availability/group/constraint/evidence/sort/view controls form an unreadable dense strip and remain visible even for an empty market.

#45 owns the presentation redesign. Read-model capabilities should not be deleted merely to simplify the first screen; controls should instead be composed progressively and responsively.

## 3. Opportunity detail

The internal detail view can compose:

- Opportunity/company header;
- Work Locations;
- Postings, Sources, Source References and ExternalLinks;
- Research Observations;
- External and Personal Assessments with provenance separation;
- Search-Profile-aware Fit breakdown;
- Availability history/freshness;
- personal Decisions/Tracking history;
- private Opportunity note;
- Group memberships;
- Duplicate Case context;
- ApplicationCase/material/document panels.

Imported evidence and private Vocation state remain visibly distinguishable.

## 4. OpportunityFitView / breakdown (implemented)

Read-only calculation for one Opportunity and one exact Search Profile revision.

Contains:

- Opportunity/Profile identity and profile revision;
- candidate revision only when candidate facts actually contribute;
- hard-constraint status;
- bounded weighted Fit score when enough evidence exists;
- Evidence Completeness;
- criterion contributions with weight/value/normalized contribution/explanation;
- explicit missing-evidence items;
- hard-constraint failures/unknowns;
- Assessment provenance where relevant.

List and detail use the same Fit implementation. There is no second UI scoring algorithm.

## 5. CandidateProfileView (implemented)

Shows the current private Candidate Profile revision and structured facts supported by the current schema.

The read model is local/private and never part of Published Vocation contracts.

Current UI exposes repeatable profile facts as form rows. #46 plans a richer durable career-profile/document workspace; planned Career/Profile documents/extraction proposals are not yet part of this current read model.

## 6. SearchProfileView (implemented)

Shows stable Search Profile identity, current revision, default state, current snapshot and Evaluation Policy.

The current snapshot exposes role/seniority/technology/location/work-model/employment/industry/salary/hard-constraint/result-target fields.

#47/#48 plan structured Search Areas and catalog-backed selectors. Historical/current raw snapshot values remain readable during any migration.

## 7. InitialResearchPromptView (implemented)

Normal Initial Research UI/read response exposes:

- selected/default Search Profile and exact revision context;
- explicit Candidate Profile inclusion state;
- as-of date;
- rendered prompt;
- opaque Initial Research `prompt_context_ref` returned separately for the linked inline import workflow;
- expected Research Bundle 1.0 contract.

Research Bundle 1.0 itself does not include the internal profile/context reference.

## 8. ImportReportView

Contains, as supported by the import type:

- Import ID/metadata;
- Bundle version/fingerprint;
- Prompt Context Ref when linked/required;
- scope;
- result/counts;
- entry results;
- structured errors/warnings;
- affected domain identities.

Rejected attempts do not expose a partially applied domain state.

## 9. Availability/Freshness views

Internal Opportunity/Posting read models expose derived Availability and age of the newest Availability evidence (`last_checked_at`, `age_days`).

Current Availability remains separate from general Research age. An old Posting can be flagged for verification by product workflow without being automatically `unavailable`.

The planned #49 freshness/company-first strategy should reuse these read semantics rather than invent a competing current-posting truth.

## 10. OpportunityComparisonView (implemented)

Read-only temporary comparison of 2–4 unique existing Opportunities in explicit requested order.

Each column includes relevant identity/work-location/tracking/availability/group information and the supported research dimensions:

- technology requirements;
- tasks;
- seniority;
- experience requirements;
- work model;
- salary;
- Opportunity-scoped Assessments.

Missing values remain explicit. Multiple evidence values remain visible and are not automatically labeled contradictory. Personal Assessment uses the current revision; external evidence retains provenance.

The comparison is not a second ranking/winner system and never mutates state.

## 11. GroupView / ApplicationWaveView (implemented internal semantics)

Group read models expose:

- stable Group ID;
- name/description/type;
- ordered membership positions;
- Opportunity summaries;
- derived status/availability summaries where useful.

`ApplicationWaveView` is the same underlying Group model for type `application_wave`, not a separate aggregate.

The first manual product pass did not accept literal `Groups/Waves` as final main-navigation language. #45/#50 may present these read models as clearer collections/application phases without changing underlying semantics silently.

## 12. ApplicationCaseView (implemented private/internal)

Shows:

- ApplicationCase identity/Opportunity relation;
- lifecycle/current state;
- append-only lifecycle history;
- active/terminal historical cases as supported;
- ApplicationMaterial metadata/current revisions;
- attached ApplicationDocument private metadata for the exact material revision.

Private document payloads/storage references do not become normal Opportunity/Public read fields.

`OpenApplicationDocument` returns exact private bytes only after integrity validation and only through the private content boundary. There is no automatic open, revision fallback or Published exposure.

#50 plans a coherent `Bewerbungen` workspace and Application Draft review state built on these primitives.

## 13. Career/ProfileDocumentView (planned, #46)

Future private profile-document list/detail should expose reusable CV/certificate/reference metadata independently of one ApplicationCase.

It may show extraction status/proposals later, but extracted facts are not current Candidate Profile facts until explicitly accepted.

## 14. ResearchCoverageView (planned, #49)

Future read model for deliberate market coverage, especially Company-first research.

Candidate fields:

- discovery Company/careers-page identity;
- last checked time;
- Research Strategy/Prompt Run provenance;
- outcome: relevant current roles / none / inaccessible / revisit;
- selected/uncovered state for next run.

Coverage state is not an imported Opportunity and does not fabricate job evidence.

## 15. MapProjection (implemented)

Internal Vocation map projection is built from an explicit Opportunity ID set, normally the same filtered set as the list.

Features represent resolved WorkLocations and include Vocation-owned job information/actions such as Opportunity/company/title/location/precision/tracking/availability/group context as defined by the implementation.

Rules:

- unresolved WorkLocations do not fabricate coordinates;
- geocoding resolution does not increase WorkLocation Research Precision;
- URLs stay outside the MapProjection;
- generic rendering/clustering/hit testing belongs to Orientation;
- action activation returns to Vocation for detail/external-link commands;
- map rendering mutates no Vocation domain state.

Future Search Profile Search Areas are separate from WorkLocation map features.

## 16. ExternalLinkView (implemented)

Derived from Posting + Source + Source Reference; no separate ExternalLink table.

Includes enough Source/URL/availability/observed/preferred context for explicit user selection/opening. Invalid/non-HTTPS links never reach the browser adapter.

The PreferredPostingSelector is deterministic; a manual selection for one open operation is not persisted as a hidden preference.

## 17. DuplicateCaseReview (implemented)

Shows:

- stable Case ID/subject type;
- readable subject summaries;
- Evidence/Source Reference summaries;
- optional import confidence;
- creation time;
- current DuplicateDecision;
- full append-only Decision history;
- reviewed/resolved state.

`keep_unresolved` is reviewed but unresolved. Other accepted outcomes classify the case but never perform merge/deletion/re-parenting.

## 18. Published Opportunity Overview 1.0 (implemented/frozen)

Client-neutral Vocation-owned Published Read Projection defined by `schemas/published-opportunity-overview-v1.schema.json` and exposed through the separate published endpoint.

Contains only the frozen contract fields/opaque refs. It excludes private state, URLs, research provenance, Availability/Freshness and writes.

## 19. Published Map Projection 1.0 (implemented/frozen)

Client-neutral URL-free map contract defined by `schemas/published-map-projection-v1.schema.json`.

Publication reads existing explicit MapLocationResolutions only; it never geocodes/mutates. It remains separate from the richer local Vocation→Orientation presentation composition.

## 20. Publication metadata

Publication metadata describes the published artifact/snapshot and its generation time according to the frozen contract. Publication age must not be confused with Posting Availability/Freshness.

## 21. Error/read resilience

A failed mutation must not unnecessarily clear previously loaded valid read state. Read-model errors should identify the failed sub-workflow where practical.

The manual acceptance also exposed a developer launcher observability problem (#52): a visible Vite page is not proof that the hidden backend started successfully. This is tooling/runtime diagnosis, not a Read Model semantic.

## 22. Product-acceptance note

The read capabilities above are substantially implemented and tested, but their current visual composition is not product-accepted. `docs/17_MANUAL_PRODUCT_ACCEPTANCE.md` records the first manual findings and the next user-facing information-architecture direction.
