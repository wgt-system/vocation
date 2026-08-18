# Vocation – Domain Model

**Status:** current through the implemented post-v0.4 Candidate/Search Profile, explainable Fit and profile-aware Initial Research capabilities. Planned product extensions are explicitly marked.

## 1. Domain model principles

- Vocation is locally authoritative for its job-market, search-strategy, fit, personal-decision and application semantics.
- External Research supplies versioned evidence/contracts, never hidden personal mutation.
- Historical/revisioned state is preserved where provenance matters.
- Stable internal/domain concepts are separated from user-facing UI wording.
- Generic capabilities such as place search/geocoding remain behind accepted system boundaries such as Orientation.

## 2. Core market aggregates

### JobOpportunity

Central personal representation of one concrete professional opportunity.

Relevant state includes:

- stable `OpportunityId`;
- canonical title;
- `CompanyId`;
- optional organization-unit relation;
- Work Locations;
- Tracking Status;
- timestamps and imported evidence relations.

Invariants:

- exactly one current Company relation;
- multiple Postings are allowed;
- `excluded` requires the corresponding personal Exclusion semantics;
- external imports never overwrite Personal Assessments, Decisions, notes, Group memberships or ApplicationCases;
- archival/history operations do not delete Research history.

### JobPosting

Concrete published representation of an Opportunity.

Relevant state:

- stable `PostingId`;
- `SourceId` and Source Reference;
- optional external posting ID;
- observed title/content evidence;
- observation times;
- Opportunity relation.

Safe deterministic identity is based on Source + external posting ID where available, otherwise the accepted normalized HTTPS-URL fallback. Similar title/company/location text alone does not authorize an automatic merge.

### Company

Evidence-backed organization in the imported Vocation market.

Relevant fields include stable identity, canonical name, alternative names, official website evidence and related organization/location information where supported by evidence.

A future Company **research-coverage candidate** from #49 is not automatically the same thing as an evidence-backed imported Company/Opportunity. Discovery coverage must not weaken import/identity rules.

## 3. External evidence and imports

### ResearchObservation

Append-only/time-bound sourced statement about a supported subject/dimension. An Observation is evidence, not timeless truth.

### ResearchImport

Audit/provenance record for one Research/Update import attempt.

Relevant state includes:

- import ID;
- bundle fingerprint/version;
- status/report;
- errors/warnings;
- optional validated Prompt Context reference when the workflow supplies one.

### Initial Research Bundle 1.0

Frozen external contract for initial market research. It does not gain Candidate/Search Profile IDs merely because profile-aware prompting exists.

### Research Update Bundle 2.0

Separate versioned external contract for scoped update of known subjects through Vocation-issued opaque Correlation References.

### Availability Check Bundle 1.0

Separate versioned external contract for append-only Availability Observations of known Postings.

## 4. Personal profile and search strategy

### CandidateProfile

Private, revisioned local representation of person/qualification facts.

The currently implemented snapshot contains headline/summary, education, skills/technologies, languages, experience summary, projects/portfolio and work-relevant interests.

Invariants:

- revisions are immutable historical snapshots;
- the newest revision is the current profile;
- profile data is not a Published Vocation Capability;
- Research includes Candidate Profile data only through an explicit prompt-disclosure choice;
- Candidate facts do not own Search Profile policy.

#46 plans a richer durable personal career model and reusable CV/certificate/evidence documents. Those are roadmap semantics, not claims about the current schema.

### SearchProfile

Vocation-owned revisioned job-search strategy with stable profile identity and immutable revisions.

The current snapshot can contain:

- name/description;
- target roles and seniority;
- preferred/acceptable/avoided technologies;
- target locations;
- accepted work models and relocation willingness;
- employment-type preferences;
- preferred/avoided industries and company characteristics;
- salary floor/target;
- must-have/must-not constraints;
- quality-first result limit;
- criterion-specific Evaluation Policy.

Invariants:

- one Search Profile may be default at a time;
- historical revisions remain immutable;
- technology tiers are mutually exclusive;
- salary floor may not exceed salary target;
- result target is bounded;
- changing current catalog terminology in future must not rewrite historical profile revisions.

### SearchArea (planned, #47)

Future structured replacement for raw location strings where useful.

A Search Area owns job-search semantics such as selected place reference/label and optional radius. Generic place lookup/geocoding is consumed from Orientation; Vocation does not become the generic place authority.

Remote, nationwide search and relocation remain separate policy concepts.

### SearchCatalogEntry (planned, #48)

Stable Vocation-owned reference item for role/technology/industry vocabulary, supporting canonical label, aliases, lifecycle status and custom entries.

Catalog evolution never silently rewrites historical Search Profile snapshots.

## 5. Assessment and explainable fit

### AssessmentCriterion

Vocation-owned semantic criterion definition with stable ID, display name/description, value type, optional range/categories, applicable subject type, activation state and display order.

Once referenced by Assessments, incompatible semantic changes require a new Criterion ID. Display metadata/activation/order remain separately editable under the accepted rules.

### ExternalAssessment

Assessment supplied through Research evidence and linked to a known Vocation Criterion.

### PersonalAssessment

Private Vocation-owned assessment with immutable revisions. Exactly one current revision exists per Opportunity/Criterion pair.

Research imports never mutate Personal Assessments.

### SearchProfileEvaluationPolicy

Search-Profile-specific criterion policy separated from the global Criterion definition.

It can contain weight and supported minimum/required semantics. Hard Search Profile must-have/must-not rules remain separate from weighted fit.

### OpportunityFit

Read-only deterministic calculation for one Opportunity and exact Search Profile revision.

Contains at least:

- Opportunity/Profile identity and revision provenance;
- hard-constraint status (`pass`, `fail`, `unknown`);
- weighted fit score when evidence permits;
- evidence completeness;
- criterion contributions/explanations;
- missing evidence and hard-constraint failures/unknowns.

Rules:

- no opaque ML ranking;
- missing evidence is visible, never silently neutral;
- Personal/External assessment provenance remains distinguishable;
- calculation has no hidden mutation;
- Candidate Profile revision is recorded only where Candidate facts actually contribute.

## 6. Personal triage

### OpportunityDecision

Append-only/traceable personal decision, including Exclusion/Restore semantics where applicable.

### TrackingStatus

Current personal triage state: `new`, `to_review`, `interesting`, `shortlisted`, `deferred`, `excluded`, `archived`.

The API/domain enum does not require literal English labels in the UI.

### OpportunityNote

One private current note per Opportunity in the current product slice. It is separate from Research Observations, Assessments and Decisions and never contributes to Fit automatically.

## 7. Prompting and provenance

### ResearchPromptRun

Documents generation of a concrete prompt.

Supported prompt families include:

- initial market research;
- full update;
- company update;
- opportunity update;
- gap filling;
- availability check.

A Prompt Run does not mutate market/domain state.

### PromptContextSnapshot

Immutable read-only snapshot of the exact Vocation context used to generate a prompt.

#### Initial Research

Post-v0.4 Initial Research **does** use a Prompt Context Snapshot.

It records:

- exact Search Profile ID/revision/snapshot;
- exact Candidate Profile revision/snapshot when explicitly included;
- as-of date;
- canonical expected Research Bundle 1.0 `research_scope`;
- opaque internal `prompt_context_ref` exposed separately to the normal inline import workflow.

Research Bundle 1.0 itself remains unchanged and contains no internal profile IDs.

A linked Initial Research import may persist the validated prompt-context reference. Legacy/manual context-free 1.0 import remains valid with no prompt provenance.

#### Update prompts

Update snapshots contain scope-local opaque Correlation References for known Companies/Opportunities/Postings according to Research Update Bundle 2.0.

Correlation References are valid only in their issuing snapshot and do not authorize ownership/re-parenting changes.

### ResearchStrategy / ResearchCoverage (planned, #49)

Future Vocation-owned metadata for explicit research methods/runs and market coverage, e.g. role-first, company-first, domain/technology, regional, freshness re-check and gap/coverage runs.

This does not silently change Research Bundle schemas. A research-coverage Company entry is discovery state, not automatically imported Opportunity evidence.

## 8. Availability/Freshness

### AvailabilityObservation

Append-only evidence for a known Posting.

Supported contract outcomes are interpreted conservatively: explicit available/unavailable evidence may derive those states; temporarily unreachable/not found/indeterminate evidence derives `uncertain` rather than automatic permanent unavailability.

### AvailabilityEvaluator

Derives current Posting/Opportunity Availability without creating a permanent Opportunity-closed truth.

### Freshness

Current implemented Freshness is age of Availability evidence, not a universal age score for all Research data.

A posting's apparent age can trigger verification, but age alone does not mutate Availability.

## 9. Groups and application planning

### OpportunityGroup

Aggregate with stable Group ID, name, optional description, type `general` or `application_wave` and ordered memberships.

Membership is mutable organization state; it never changes Opportunity identity, tracking, Assessments, Decisions, Research or Availability.

### ApplicationWave

`OpportunityGroup` with type `application_wave`, not a separate aggregate. It has no automatic submission/deadline/status semantics.

The manual acceptance rejected literal `Groups/Waves` as final product language. #45/#50 may present the same underlying semantics through clearer collection/application-planning concepts.

## 10. Application domain

### ApplicationCase

Vocation-owned Aggregate for one Opportunity with independent application lifecycle.

V1 lifecycle:

`draft` → `ready` → `submitted` → `interviewing` → `offer`, with terminal `accepted`, `rejected`, `withdrawn` according to the implemented transition rules.

Invariants:

- creation/transitions are explicit user actions;
- at most one active/nonterminal case per Opportunity;
- terminal cases remain historical;
- Opportunity Tracking Status is independent;
- Research/Availability/Groups never create or mutate ApplicationCases;
- no automatic submission.

### ApplicationMaterial

Private material metadata owned by an ApplicationCase with stable Material ID, kind (`cv`, `cover_letter`, `other`), display name and explicit revisions.

Material revisions are historical. Actual immutable payload content can be attached through `ApplicationDocument`; the older pre-document-slice statement that content is undefined is obsolete.

### ApplicationDocument

Private immutable content attached to exactly one ApplicationMaterial revision.

Metadata includes Document ID, material/revision identity, original filename, media type, byte size, SHA-256 digest and creation time. Current accepted media types are `application/pdf`, `text/plain`, `text/markdown`.

Payload replacement requires a new Material revision. Missing/corrupt backing payload is an explicit integrity error.

### ApplicationDocumentStore

Provider-neutral infrastructure port for private bytes and opaque storage references. Physical path/layout is not domain semantics.

### CareerProfileDocument (planned, #46)

Reusable private career document such as CV/certificate/reference, not semantically owned by exactly one ApplicationCase.

The planned implementation should reuse compatible document-integrity/storage infrastructure without pretending a reusable profile document is already an ApplicationMaterial revision.

### DocumentExtractionProposal (planned, #46)

Extracted text/fact proposal with provenance. It is not a confirmed Candidate Profile fact until explicitly accepted.

Document extraction starts behind a replaceable port; a separate generic PDF/OCR service requires a separately justified architecture boundary.

### ApplicationDraft (planned, #50)

Externally/generated private draft (e.g. cover letter/application message) from an exact Opportunity/Profile/document context. It becomes accepted ApplicationMaterial only through explicit review/action; generation never means submission.

## 11. Identity and duplicate review

### DuplicateCase

Persisted possible-identity relationship between two supported subjects with evidence. It never performs automatic merge.

### DuplicateDecision

Implemented append-only personal review history for a DuplicateCase with outcomes:

- `confirmed_duplicate`;
- `confirmed_distinct`;
- `related_but_distinct`;
- `keep_unresolved`.

A nonblank reason is required. Latest decision is current judgment. `confirmed_duplicate` is classification only and performs no merge, deletion, re-parenting or transfer of Assessments/Decisions/Groups/Application state/documents.

## 12. Spatial supporting data

### WorkLocation

Research/Vocation fact about where an Opportunity is performed.

### MapLocationResolution

Current Vocation-owned supporting resolution for one WorkLocation with coordinates, source (`manual`/`geocoder`), optional provider key, resolved time and query/label.

It is neither Research Evidence nor Decision history. Geocoding cannot increase the underlying WorkLocation Precision.

### MapProjection

Read-only projection built from the currently selected/filtered Opportunity set. Generic rendering/place capability is delegated to Orientation; Vocation owns job-specific feature/action meaning.

## 13. External links

### ExternalLink

Derived read/application value from Posting + Source + Source Reference. No own persistence table.

Policy accepts only structurally valid absolute HTTPS URLs with host. No automatic network probing is performed as part of URL validation.

### PreferredPostingSelector

Deterministically ranks valid link candidates using the accepted order:

1. Availability `available > unknown > uncertain > unavailable`;
2. Source Type `company_careers > job_board > professional_network > other`;
3. newest observed time;
4. Posting ID tie-break.

Opening remains an explicit user action.

## 14. Publication

### Published Opportunity Overview 1.0

Frozen client-neutral Vocation-owned read contract. It contains only its schema-defined fields/opaque refs and no private state, URLs or hidden write semantics.

### Published Map Projection 1.0

Frozen client-neutral URL-free map projection contract based on already resolved locations. Publication does not geocode or mutate state.

Publication age is not Posting Freshness/Availability.

## 15. Important repositories/ports

Representative persistence/application boundaries include repositories/services for:

- Opportunities/Postings/Companies;
- Research imports and prompt contexts/runs;
- Assessments/Decisions/notes;
- Candidate/Search Profiles;
- Groups;
- Duplicate Cases/Decisions;
- Availability;
- ApplicationCases/Materials/Documents;
- map resolutions/read models;
- Published projections.

Application logic depends on explicit repository/infrastructure ports rather than UI widgets or physical file paths.

## 16. Read models

Important current read models include:

- Opportunity list/detail/workspace;
- Search Profile-aware Fit breakdown;
- Opportunity comparison;
- map projection;
- group/duplicate/application views;
- import reports and prompt workflow state;
- published projections.

Filtering/search/sorting read behavior does not mutate personal/domain state.

## 17. Planned post-acceptance model work

The first manual product pass does not invalidate the implemented v0.4/post-v0.4 model. It identifies model/presentation extensions tracked separately:

- #46 richer personal career profile/documents/extraction proposals;
- #47 structured Search Areas and typed Search Profile editors;
- #48 maintainable search vocabularies;
- #49 explicit Research Strategy/Coverage state;
- #50 coherent application drafting/workspace.

`docs/17_MANUAL_PRODUCT_ACCEPTANCE.md` is authoritative for the current release gate and for which of these concepts are planned versus implemented.
