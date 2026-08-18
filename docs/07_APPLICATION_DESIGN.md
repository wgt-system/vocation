# Vocation – Application Design

**Status:** current through the implemented post-v0.4 personal-search, fit and profile-aware research baseline. Planned product work is marked explicitly.

## 1. Purpose

The Application Layer coordinates Vocation domain objects, persistence ports and infrastructure adapters. It owns use-case orchestration and transaction boundaries but must not hide core Vocation rules in controllers or UI components.

Version 1 remains a local single-user product; there is no general account/role system.

## 2. Candidate and Search Profile use cases

Implemented application operations support:

- read/update current Candidate Profile through immutable revisions;
- list/read/create/update/delete Search Profiles;
- select exactly one Search Profile as default;
- persist immutable Search Profile revisions;
- maintain Search-Profile-specific evaluation policy;
- calculate/read explainable Opportunity Fit for an explicit/default Search Profile.

Profile mutations never publish private data automatically and do not start external research implicitly.

Planned #46/#47/#48 work may add structured Career/Profile documents, Search Areas and catalog-backed editors. Those are separate accepted use cases, not silent reinterpretations of existing snapshots.

## 3. Assessment criteria and personal triage commands

### Criteria management

Vocation manages its own Assessment Criterion catalog. Incompatible semantic changes to an already referenced Criterion are rejected and require a new Criterion ID.

### Create/RevisePersonalAssessment

Create establishes the first current Personal Assessment for Opportunity/Criterion; revise creates a new immutable revision and only accepts the current revision as predecessor.

### ChangeTrackingStatus

Explicit personal command. External imports never invoke it.

### ExcludeOpportunity / RestoreOpportunity

Exclusion requires a nonblank reason and creates historical Decision state. Restore references the active Exclusion and defaults to its saved previous status unless an explicit valid alternative is provided.

### Opportunity notes

Private note create/update/clear is separate from Assessments/Decisions and never affects Fit automatically. Research/Update imports preserve it.

## 4. Generate Initial Research Prompt (implemented)

Input:

- explicit Search Profile ID or configured default;
- as-of date;
- explicit include/exclude Candidate Profile choice.

Flow:

1. resolve the exact Search Profile and revision;
2. optionally resolve the exact current Candidate Profile revision;
3. build an immutable Initial Research Prompt Context Snapshot;
4. record the structured Search Profile snapshot, optional Candidate snapshot, as-of date and canonical expected Research Bundle 1.0 `research_scope`;
5. load the versioned Initial Research template and output-contract guidance;
6. render a quality-first prompt that prioritizes evidence for Search Profile constraints/policy without asking external research to own Vocation ranking or private state;
7. persist the prompt-context/provenance state;
8. return prompt text plus opaque `prompt_context_ref` separately from the frozen Research Bundle contract.

Output includes:

- rendered prompt;
- opaque Initial Research prompt-context reference;
- selected profile/revision context needed by the UI;
- expected Research Bundle version 1.0.

Rules:

- no freeform profile re-entry is required in the normal flow;
- Candidate Profile data is included only after explicit choice;
- Research Bundle 1.0 remains unchanged and contains no internal profile IDs;
- prompt generation mutates no market/personal decisions.

## 5. Generate Update/Gap/Availability Prompt (implemented)

Supported update prompt modes:

- Full Update;
- Company Update;
- Opportunity Update;
- Gap Filling;
- Availability Check through its dedicated contract/workflow.

Update flow:

1. validate explicit scope;
2. resolve known subjects;
3. build the minimum immutable Prompt Context Snapshot;
4. issue scope-local opaque Correlation References where Research Update Bundle 2.0 requires them;
5. embed only required context and generic protected-state rules;
6. render/persist prompt provenance;
7. expose preview/copy/save to the user.

Correlation References do not reveal/replace ownership relationships and are valid only for the issuing snapshot.

Availability Check remains separate from Research Update Bundle 2.0 and requests only supported availability evidence for known Postings.

## 6. Import Initial Research Bundle 1.0

Input:

- JSON/file/clipboard payload;
- optional internal `prompt_context_ref` supplied separately by the normal linked Initial Research UI flow.

Flow:

1. read/parse JSON;
2. validate frozen Research Bundle 1.0 schema/semantics;
3. fingerprint and duplicate-import check;
4. when a prompt-context reference is supplied, resolve it as an Initial Research context and validate the returned canonical `research_scope` exactly;
5. translate through the Vocation import ACL;
6. build deterministic domain mutation plan and detect blockers;
7. apply the accepted plan atomically;
8. persist import/provenance report including prompt-context linkage where supplied.

Legacy/manual context-free 1.0 imports remain supported and keep null prompt provenance.

## 7. Import Research Update Bundle 2.0

Flow:

1. parse and validate 2.0 contract;
2. resolve required Prompt Context Snapshot;
3. validate scope and supplied Correlation References before mutation;
4. resolve deterministic posting/subject identity;
5. build deterministic update plan;
6. reject all blockers before apply;
7. perform one atomic apply;
8. preserve historical external evidence and all protected personal state;
9. persist report/provenance.

Updates never contain/mutate Candidate/Search Profiles, Personal Assessments, Decisions, Tracking Status, notes, Groups/Waves or ApplicationCases/Materials/Documents.

## 8. Availability workflow

Availability Check generation/import is explicit and append-only.

The evaluator derives current Posting/Opportunity Availability from the newest supported observations. Temporarily unreachable/not found/indeterminate does not become permanent `unavailable`.

Manual research strategy work may trigger more frequent/targeted freshness re-checks (#49), but it reuses this ownership boundary rather than inventing a parallel availability truth.

## 9. Duplicate review (implemented)

### ResolveDuplicateCase

Input:

- existing Duplicate Case ID;
- outcome `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` or `keep_unresolved`;
- nonblank reason.

Flow:

1. load existing case/subject/evidence summary;
2. reject invalid/no-op current outcome as specified;
3. append a new sequenced DuplicateDecision;
4. return current review state/history.

No outcome performs merge, deletion, canonical-survivor selection, re-parenting or transfer of Assessments/Decisions/Groups/Application state/documents.

## 10. Groups/Application Waves (implemented domain/application capability)

Commands:

- Create/Edit/Delete OpportunityGroup;
- Add/Remove Opportunity membership;
- Reorder complete member set deterministically.

Group mutations affect only group metadata/membership. They never mutate Opportunity research/personal/application state.

The manual product pass rejected `Organisation`/literal `Groups/Waves` as final main-navigation language. #45/#50 may compose these use cases into clearer collection/application-planning presentation without changing commands invisibly.

## 11. ApplicationCase and private documents (implemented)

### ApplicationCase commands

- create ApplicationCase for an Opportunity;
- change lifecycle explicitly;
- create ApplicationMaterial metadata;
- create a new Material revision.

ApplicationCase lifecycle remains independent from Opportunity Tracking Status. No Research/Availability/Group event creates or advances an ApplicationCase automatically.

### ApplicationDocument attach/read

`ApplicationDocumentService` attaches supplied bytes to an exact immutable Material revision:

1. reject an already occupied revision;
2. derive private semantic metadata from supplied bytes;
3. allocate opaque storage reference;
4. write payload through `ApplicationDocumentStore`;
5. read back and verify byte size/SHA-256;
6. only then persist metadata/reference.

Read flow resolves metadata, reads exact payload and verifies integrity before returning private bytes/media type. Storage reference/physical path never leaves the service boundary.

Current private internal endpoints support material-revision document metadata/attach and document content open access. Current media types are PDF, plain text and Markdown.

The earlier application slice limitation “document content not implemented” is obsolete; upload and explicit read-only open access are implemented.

## 12. Planned persistent Career/Profile documents and extraction (#46)

A reusable CV/certificate/reference library is not the same ownership relation as an `ApplicationDocument` attached to one ApplicationMaterial revision.

Planned use cases should:

- persist reusable private career documents once;
- reuse compatible Vocation document storage/integrity primitives;
- associate documents to the personal profile and later application flows explicitly;
- introduce a provider-neutral Document Extraction port only when extraction is implemented;
- present extracted facts as reviewable proposals with provenance;
- create Candidate Profile revisions only after explicit user acceptance.

No separate PDF/OCR microservice is implied by this application design. That boundary requires system-level reuse/runtime justification.

## 13. Planned structured Search Profile editing (#47/#48)

Application use cases may expose:

- search/filter role/technology/industry catalog entries;
- create explicit custom values;
- select seniority/employment types through controlled enums/catalogs;
- resolve generic places through Orientation-backed place search;
- create/update Search Areas with optional radius;
- persist the resulting exact Search Profile revision.

The UI must not silently mutate a profile while merely searching/selecting catalog options.

## 14. Planned Research Strategy/Coverage use cases (#49)

Expected explicit operations include starting/generating a research run for:

- role-first discovery;
- company-first career-page coverage;
- domain/technology discovery;
- regional phase;
- freshness re-check;
- gap/coverage work.

Vocation may persist Research Coverage (e.g. which companies were checked and when) independently from imported evidence-backed Opportunities. A zero-result company check is still useful coverage state.

External research remains copy/paste/user-initiated; there is no crawler requirement.

## 15. Planned application workspace/draft generation (#50)

From an explicit ApplicationCase/Opportunity the user may:

1. select exact Candidate Profile revision and relevant local facts/documents;
2. preview the private context that will be disclosed;
3. generate/copy a versioned application-material prompt;
4. receive external draft text;
5. review/edit/accept it explicitly;
6. create a new private ApplicationMaterial revision only after acceptance.

Initial draft targets include cover letter/application message/tailored summary. There is no automatic application submission.

## 16. External link open workflow (implemented)

`OpenPostingInBrowser`:

1. derive valid ExternalLink candidates;
2. use explicit user selection or deterministic PreferredPostingSelector;
3. validate via ExternalLinkPolicy;
4. pass only accepted HTTPS URL to OS browser adapter;
5. surface local error if opening fails.

No link opens because a page/map/filter merely rendered.

## 17. Queries/read models

Current read/application queries include:

- Opportunity list/workspace and detail;
- Candidate/Search Profile state;
- Search-Profile-aware Opportunity Fit;
- groups/memberships;
- Duplicate Cases/Decisions;
- ApplicationCases/Materials/Documents;
- comparison of 2–4 Opportunities;
- map projection for an explicit Opportunity set;
- prompt preview/import reports;
- Published Opportunity Overview and Published Map Projection through separate publication boundaries.

Opportunity workspace filtering/search/sort combines text, tracking, availability, group, hard-constraint/evidence and Search Profile fit context without hidden mutation.

## 18. Map application flow

Vocation produces job-specific MapProjection/read data. Generic rendering/Place Search belongs to Orientation.

Current explicit WorkLocation resolution flow uses Vocation `Geocoder` port → `OrientationGeocoder` → Orientation Place Search. `OrientationMapFrame` adapts Vocation-owned scene/action information to the pinned Orientation Embed Host.

Future Search Area place selection (#47) should reuse Orientation Place Search without conflating Search Area and WorkLocation.

## 19. Publication

Published Opportunity Overview 1.0 and Published Map Projection 1.0 are frozen, read-only, client-neutral Vocation-owned contracts. They remain separate from internal React OpenAPI and from private Candidate/Search/Application state.

Future private cross-device access requires an explicit protected boundary; it does not make WGT/Conveyance owners of Vocation commands.

## 20. Transaction/error rules

- each personal command is atomic;
- accepted Research/Update bundle application is atomic after blocker validation;
- no documented “partial import” is silently introduced;
- errors carry a stable code/user message and enough context/recoverability information to fix the action;
- a mutation failure should remain local to the action instead of replacing the whole product screen where practical.

## 21. Current UI acceptance

The current UI implements the capabilities above, but the first manual product pass rejected major presentation choices. `docs/17_MANUAL_PRODUCT_ACCEPTANCE.md` and #45–#50 define the accepted next product direction.

Application design should therefore preserve the use cases/invariants while allowing the presentation layer to replace the current `Nächster Schritt`, `Profil & Suche`, `Organisation` and dense Stellenmarkt layout with clearer user-intent-oriented flows.
