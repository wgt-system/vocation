# Vocation – Personal Search Context

**Status:** domain/persistence/research/fit capabilities implemented on `dev`; manual product UX not yet accepted.

## Purpose

Vocation is a quality-first personal job-market application. Job relevance requires explicit knowledge of both:

1. the candidate's private qualification facts; and
2. the current Vocation-owned job-search strategy.

These concepts remain separate because facts about a person are not the same thing as the goals and trade-offs of one particular search.

## Candidate Profile

`CandidateProfile` is private local state containing qualification facts that can inform external research and later Vocation-owned evaluation.

The currently implemented model contains:

- headline and summary;
- education/degree facts;
- skills/technologies with an explicit familiarity level and optional note;
- languages and proficiency description;
- experience summary;
- project/portfolio highlights with technologies;
- general work-relevant interests.

Candidate Profile changes create immutable numbered revisions. The application reads the newest revision as the current profile.

Candidate Profile is not a Published Vocation Capability. It must not be exposed through Opportunity Overview, Map Projection, public examples, Research Bundle fixtures or other public surfaces.

### Manual-acceptance finding

The current model was sufficient to prove revision/provenance semantics but is not yet accepted as a durable personal career profile. #46 extends the product direction toward structured contact/application data, dated education and experience records, reusable CV/certificate/reference documents and a more efficient profile workspace.

The user should enter durable person facts once and reuse them across many Search Profiles and applications rather than duplicating them into every search strategy.

### Document and extraction boundary

Vocation already owns private `ApplicationDocument` content/storage semantics for application material. Reusable profile/career documents should reuse compatible local integrity/privacy infrastructure where appropriate instead of creating an unrelated file store.

Document parsing is deliberately staged:

1. local upload/storage and manual structured profile editing;
2. a replaceable document-text/extraction application port when extraction is implemented;
3. extracted facts are proposals with provenance and explicit user acceptance;
4. a separate generic document-understanding/PDF/OCR service is justified only by another concrete consumer or materially distinct runtime/security/dependency requirements.

Vocation remains authoritative for deciding what extracted text means as a Candidate Profile fact. Extraction never silently overwrites the profile.

## Search Profile

`SearchProfile` is Vocation-owned job-search strategy. Multiple named Search Profiles may coexist; one profile may be selected as the current default.

The currently implemented snapshot contains:

- name and description/strategy text;
- target roles;
- target seniority;
- preferred, acceptable and avoided technologies;
- target locations;
- accepted work models (`remote`, `hybrid`, `on_site`);
- relocation willingness;
- employment-type preferences;
- preferred/avoided industries;
- preferred/avoided company characteristics;
- optional salary floor and target with currency;
- explicit must-have constraints;
- explicit must-not constraints;
- a quality-first result limit;
- per-profile criterion evaluation policy introduced by #33.

Search Profile changes create immutable numbered revisions. The current revision is referenced by the stable Search Profile ID.

Technology preference tiers are mutually exclusive. Salary floor may not exceed salary target. Result limit is bounded to 1–50.

## Evaluation Policy and Opportunity Fit

The evaluation work from #33 is implemented.

A Search Profile owns criterion-specific policy such as weights and supported hard/required semantics without changing the global `AssessmentCriterion` definition. `OpportunityFit` is deterministic and explainable, separates hard-constraint state from weighted fit, reports evidence completeness and keeps missing evidence visible.

Candidate Profile revision provenance is recorded only where candidate facts actually contribute to the calculation; fit must not invent provenance for unused candidate data.

Hard must-have/must-not constraints remain distinct from weighted fit. Missing evidence is never silently treated as a match.

See `15_OPPORTUNITY_FIT.md` for the fit rules.

## Profile-aware Initial Research

The profile-aware research work from #36 is implemented; it is no longer a future capability.

Initial Research:

- selects an explicit Search Profile or the configured default;
- snapshots the exact Search Profile revision used;
- optionally includes the current Candidate Profile and records its exact revision/snapshot;
- records an as-of date and canonical expected Research Bundle 1.0 `research_scope`;
- persists an opaque `prompt_context_ref` separately from the Research Bundle;
- keeps Research Bundle 1.0 schema-compatible and free of Vocation-internal profile IDs;
- validates the returned bundle's scope against the prompt context when the normal linked inline-import path is used;
- still supports legacy/manual context-free Research Bundle 1.0 imports.

The prompt is quality-first: it prefers fewer well-evidenced current opportunities to quota-filled weak results and prioritizes evidence needed by the selected search/evaluation policy.

## Ownership

Vocation owns:

- search intent and strategy;
- role and seniority targets;
- geographic search-area meaning, radii and employment/work-model preferences;
- must-have and exclusion semantics;
- technology and industry preference tiers;
- salary/search-result policy;
- criterion weights, hard constraints, fit and ranking/explanation semantics;
- future search-strategy catalogs and research coverage state.

Candidate facts do not own those decisions.

Generic place search/geocoding is not Vocation taxonomy data. Orientation remains authoritative for generic geospatial/place capability; Vocation may consume it to resolve Search Profile places while retaining ownership of the job-search meaning of those selected areas.

## Persistence

Migration `0014` introduced:

- `candidate_profile_revisions`;
- `search_profiles`;
- `search_profile_revisions`.

Later post-v0.4 migrations add the evaluation and prompt-context persistence needed by #33/#36.

Revision payloads are persisted as structured JSON snapshots inside the local SQLite database. This preserves exact historical search/profile states without prematurely normalizing every CV/profile attribute into a separate table.

Exactly one Search Profile may be marked as default at a time.

Future structured profile/catalog work may normalize selected repeated concepts where stable identity/query behavior is useful, but historical revisions must remain deterministic and readable.

## Internal API

Private React API includes Candidate/Search Profile CRUD/default operations plus the fit and profile-aware prompt boundaries. These are internal Vocation APIs and are not Published Contracts.

The core profile endpoints include:

- `GET /api/profiles/candidate`
- `PUT /api/profiles/candidate`
- `GET /api/profiles/search`
- `GET /api/profiles/search/default`
- `GET /api/profiles/search/{profile_id}`
- `POST /api/profiles/search`
- `PUT /api/profiles/search/{profile_id}`
- `POST /api/profiles/search/{profile_id}/default`
- `DELETE /api/profiles/search/{profile_id}`

Generated OpenAPI/TypeScript types remain the source for the internal frontend contract.

## Presentation: implemented vs accepted direction

The current React application exposes `Profil & Suche` with **Mein Profil**, **Suchprofile** and evaluation-policy controls. Repeatable Candidate Profile facts use form rows, while several Search Profile list values are currently edited as newline-delimited text.

The first manual product pass rejected that presentation as too form-heavy and inconsistent. It is important not to describe it as final UX merely because the backend semantics are implemented.

Current accepted direction:

- likely user-facing top-level label **Profile** rather than `Profil & Suche`;
- personal profile, search profiles and evaluation remain separate subareas under one coherent workspace;
- target roles, seniority, employment types, technologies and industries use searchable typed selectors/chips rather than normal multiline textareas;
- target locations become explicit Vocation Search Areas selected through Orientation-backed place search, with optional radii where appropriate;
- custom role/technology/industry terms remain possible;
- `Ziel & Schwerpunkt` is replaced/clarified as explicit structured priorities where possible plus one optional qualitative strategy note for nuance.

#47 owns the structured editor/search-area work. #48 owns maintainable Vocation role/technology/industry catalogs and prompt-assisted, explicitly reviewed catalog proposals.

## Relationship to real-market research

A Search Profile defines what is relevant; it does not prescribe only one discovery algorithm.

Manual job-search work showed that direct company-career-page inspection, domain/technology discovery, regional phases and freshness re-checks can produce materially better coverage than one broad role/location query. #49 introduces explicit Research Strategies/Runs so multiple deliberate discovery grinds can reuse the same Search Profile without changing its semantic preferences.

Search breadth and acceptance quality remain separate: a research run may inspect many companies and return only a few well-evidenced Opportunities.

## Relationship to applications

Candidate Profile facts are reusable input for application work but are not themselves an `ApplicationCase` or `ApplicationMaterial`.

#50 plans a user-facing application workspace and explicit prompt-assisted application drafts from an exact Opportunity/Profile/document context. Generated text remains a reviewable private draft; there is no automatic submission or silent external disclosure.

## Product-acceptance status

The technical Candidate/Search Profile, fit and profile-aware research slices are complete and regression-tested. The current UI/data-entry experience is not yet product-accepted. The manual findings and release implications are recorded in `17_MANUAL_PRODUCT_ACCEPTANCE.md` and parent issue #42.
