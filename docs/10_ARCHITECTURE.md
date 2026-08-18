# Vocation – Architecture

**Status:** Version-1 architecture remains accepted; this document is aligned with the implemented post-v0.4 personal-search baseline and the current manual-acceptance direction.

## 1. Architecture goals

- independently runnable local Vocation product;
- clear Domain / Application / Infrastructure / Presentation boundaries;
- Vocation-owned local persistence and business authority;
- versioned external Research/Update/Availability contracts;
- versioned client-neutral Published Read contracts;
- reuse accepted system-wide generic capabilities instead of duplicating them;
- private personal/application data remains local unless explicitly disclosed/published through a reviewed boundary;
- low operational/maintenance cost;
- no service split merely for code organization.

## 2. Version-1 runtime picture

```text
Browser/Desktop UI
      │
Internal FastAPI Presentation API
      │
Application Layer
      │
Domain Model
      │
Repositories / Query Services / Ports
      │
SQLite + private local document storage
```

Additional adapters/boundaries include:

- File/Clipboard;
- OS browser launcher;
- Orientation Place Search adapter for generic geospatial resolution;
- Orientation Host Bridge/Embed Host for generic map rendering;
- private `ApplicationDocumentStore`;
- future replaceable Document Extraction port only when #46 implements extraction.

FastAPI may serve the built frontend in production mode. The browser UI is a presentation shell around one local Vocation authority, not a distributed frontend/backend ownership split.

## 3. Technology decision

Current Vocation runtime/tooling:

- Python >=3.13, development/type/lint target 3.13;
- FastAPI and Pydantic;
- SQLAlchemy 2 and Alembic;
- SQLite;
- JSON Schema Draft 2020-12 validation;
- pytest, Ruff, mypy;
- React, TypeScript, Vite;
- Vitest, React Testing Library and Biome.

Generic map rendering/geocoding provider technology is intentionally not a Vocation technology decision. Vocation consumes Orientation-owned capabilities through explicit provider-neutral Vocation boundaries.

The application remains suitable for later local packaging (e.g. PyInstaller) without making Docker/cloud infrastructure part of the product baseline.

## 4. Layers

### Domain

Owns Vocation semantics/invariants:

- Opportunity/Posting/Company/evidence;
- Candidate/Search Profile separation;
- Search Profile policy and explainable Fit;
- personal Assessment/Decision/Tracking/notes;
- Availability/Freshness derivation;
- Groups/Application Waves;
- ApplicationCase/Material/Document semantics;
- Duplicate Case/Decision semantics;
- job-specific spatial meaning.

No FastAPI/SQLAlchemy/React/Orientation provider DTO dependencies.

### Application

Owns use-case orchestration:

- commands/queries;
- transaction boundaries;
- prompt context generation/provenance;
- import planning/application;
- Fit calculation orchestration;
- document integrity/application services;
- provider-neutral ports (`Geocoder`, `ApplicationDocumentStore`, future `DocumentExtractor`).

### Infrastructure

Implements:

- SQLAlchemy/Alembic persistence;
- filesystem private document store;
- JSON/files/clipboard;
- OS browser launch;
- Orientation adapters;
- logging/configuration;
- future concrete PDF/text/OCR extraction adapters behind an application port.

### Presentation

Includes:

- React product UI;
- internal FastAPI `/api/...` presentation API and generated TS types;
- Vocation-owned separate `/published/...` adapters for frozen client-neutral contracts;
- Vocation→Orientation scene/host adaptation for local map UI.

Internal OpenAPI is not automatically a Published WGT contract.

## 5. Persistence and private data

Vocation owns its database. No other context reads/writes it directly.

Properties:

- schema created/evolved only by Alembic migrations;
- transactional writes;
- stable internal IDs;
- imported evidence and personal state remain distinguishable;
- immutable/revisioned history where semantics require it;
- read models are projections, not persisted truth by default;
- normal private data paths are gitignored.

Private ApplicationDocument payload bytes are stored outside relational tables through `ApplicationDocumentStore`; relational metadata stores opaque storage reference plus semantic integrity metadata.

The same physical infrastructure may be reused by future Career/Profile documents, but their ownership model must not be faked as an ApplicationMaterial revision if they are reusable independently of an ApplicationCase.

## 6. Candidate/Search Profile architecture

Candidate facts and Vocation search policy are deliberately separate.

Current local persistence stores immutable Candidate Profile revisions and stable Search Profiles with immutable revisions/default selection.

Why no separate Personal Profile service yet:

- there is currently one concrete owner/consumer need inside Vocation;
- a separate runtime would add integration/deployment/security cost without a demonstrated second bounded context;
- the model is already separable enough to extract later if another concrete WGT consumer needs the same personal-profile semantics.

Search Profile-specific policy/fit remains Vocation Core Domain even if Candidate facts are ever extracted.

Future Search Areas (#47) use Orientation for **generic place lookup**, but Vocation persists/owns selected search-area/radius/remote/relocation semantics.

## 7. Prompt contexts and provenance

Prompt templates are versioned under `prompts/`.

### Initial Research

Post-v0.4 Initial Research has an immutable Vocation Prompt Context Snapshot containing:

- exact Search Profile identity/revision/snapshot;
- optional exact Candidate Profile revision/snapshot after explicit inclusion;
- as-of date;
- canonical expected Research Bundle 1.0 scope;
- opaque internal prompt-context reference.

The reference is returned separately to the internal UI/import workflow; it is not added to frozen Research Bundle 1.0.

A linked 1.0 import validates the returned scope against the snapshot and may persist prompt-context provenance. Manual/context-free 1.0 import remains supported.

### Update prompts

Update Prompt Context Snapshots contain scope-local opaque Correlation References for known subjects. Update Bundle 2.0 echoes only those references and must validate scope/identity before mutation.

`ResearchImport` records prompt-context provenance where the selected workflow supplies/requires it; external contracts do not need internal Prompt Run IDs.

## 8. Import architecture

```text
File / Clipboard / Inline JSON
  → Parse
  → Explicit contract/version dispatch
  → JSON Schema validation
  → semantic/protected-field validation
  → Prompt Context + scope validation where applicable
  → deterministic identity resolution
  → deterministic mutation plan
  → blocker check
  → one atomic apply
  → Import Report / provenance
```

Rules:

- 1.0 Initial, 2.0 Update and Availability contracts are explicitly separated;
- blockers are discovered before business mutation;
- no partial silent apply;
- Research Bundle DTOs are not database/domain entities;
- deterministic Posting identity does not become fuzzy merge;
- possible duplicates remain evidence/review cases;
- external imports never own private Profile/Decision/Note/Group/Application state.

## 9. Availability/freshness architecture

Availability is a dedicated append-only evidence boundary.

The application derives current Posting/Opportunity Availability from the newest supported Availability Observations. Temporarily unreachable/not-found/indeterminate results remain uncertain rather than creating irreversible closure.

Current `Freshness` is age of Availability evidence, not a universal age score over all Research data.

The planned research-strategy work (#49) may trigger targeted freshness re-checks but must reuse this boundary rather than add another truth source.

## 10. Map and Orientation architecture

System-wide generic geospatial capability belongs to Orientation.

Implemented split:

- Vocation owns WorkLocation, Precision, MapLocationResolution, internal MapProjection, job information/actions;
- Vocation Application owns provider-neutral `Geocoder` port;
- `OrientationGeocoder` consumes Orientation Place Search and maps only required generic result into Vocation application values;
- `OrientationMapFrame` converts Vocation-owned feature/information/action data into an Orientation Spatial Scene;
- pinned Orientation Embed Host renders generic map UI through `orientation.host-bridge` 1.0;
- action activation returns to Vocation, which owns detail navigation and ExternalLink commands.

Orientation never becomes authority for Opportunity, Search Profile, WorkLocation, Precision, Availability or ExternalLink selection.

Published Map Projection 1.0 is a separate frozen Vocation contract and is not the same thing as local Orientation scene composition.

## 11. External browser navigation

```text
Vocation link candidates
  → PreferredPostingSelector / explicit user selection
  → ExternalLinkPolicy
  → OperatingSystemBrowserLauncher
```

Rules:

- only structurally accepted absolute HTTPS URLs reach launcher;
- no automatic open on render/import/filter/map selection;
- browser adapter does not decide preferred Posting;
- Orientation only returns Vocation-owned action references, never chooses/opens external URLs itself.

## 12. ApplicationCase / document architecture

Implemented chain:

```text
ApplicationCase / ApplicationMaterial Domain
  → Application services
  → SQLAlchemy repositories / SQLite
  → internal FastAPI API
  → typed React client
```

Private content:

```text
ApplicationDocument semantic metadata
  → ApplicationDocumentService
  → ApplicationDocumentStore port
  → FilesystemApplicationDocumentStore
```

Document attach is create-only for one exact immutable Material revision and verifies byte size/SHA-256 before accepting metadata. Reads revalidate integrity. Physical paths/storage refs are infrastructure detail and are not exposed through normal API/domain/publication.

Current explicit private content endpoint/open action is not a Published contract, export/sync or cross-device access.

## 13. Future Career/Profile document extraction boundary (#46)

A CV/certificate PDF reader is **not automatically a microservice**.

Initial architecture when extraction is implemented:

```text
Candidate/Profile Use Case
   │
DocumentExtractor port
   │
local replaceable extractor adapter
   ├─ native PDF text/layout parser
   └─ OCR path for scanned documents where needed
   │
DocumentExtractionProposal + provenance
   │
explicit user review/accept
   │
new Candidate Profile revision
```

Rules:

- Vocation owns the interpretation into Candidate/Profile/Application semantics;
- extracted output is proposal/evidence, not truth;
- no silent overwrite;
- parser/OCR dependency details stay behind the port;
- document content is disclosed externally only through an explicit reviewed workflow.

A separate generic WGT Document-Understanding service/context is justified only if at least one of these becomes concrete:

1. another bounded context needs the same generic extraction capability;
2. extraction needs materially different runtime/dependencies (e.g. heavyweight OCR/ML lifecycle) whose isolation has operational value;
3. a distinct security/deployment boundary is required.

“PDF is a separate technical concern” alone is not enough.

## 14. Future structured search vocabularies (#47/#48)

Vocation may own stable reference catalogs for search-domain vocabulary (roles, technologies, industries, controlled employment/seniority values).

Catalogs are local Vocation reference data, not an external truth service. Custom entries remain possible. Prompt-assisted maintenance may propose additions, but accepted catalog mutations are explicit user/Vocation actions.

Generic geographic place data is excluded and remains Orientation-owned.

## 15. Future Research Strategy/Coverage architecture (#49)

Research Strategy describes how an external research run is performed; Search Profile continues to define what is desirable.

Potential persistent supporting state:

- Research Run/Strategy metadata;
- Company/career-page discovery coverage;
- last checked/provenance/outcome;
- under-covered scopes for future runs.

A discovery Company/coverage record must not bypass Research Bundle identity/evidence rules to become an imported Opportunity.

No crawler/paid LLM runtime is required. Explicit prompt/copy/paste remains a valid adapter boundary.

## 16. Future Application Draft generation (#50)

Application Draft prompting may combine exact snapshots of:

- selected Opportunity evidence;
- Candidate Profile revision;
- explicitly selected private document/fact context;
- user-selected tone/template constraints.

The user sees what private context will be disclosed. External returned text remains a Draft until explicitly accepted into a new private material revision.

No automatic submission, email sending or hidden lifecycle transition is introduced.

## 17. Data Publication / cross-device

Vocation owns versioned Published Read capabilities.

Current frozen contracts:

- `Published Opportunity Overview 1.0`;
- `Published Map Projection 1.0`.

They remain outside internal React OpenAPI and do not expose private Candidate/Search/Application state.

WGT/other consumers never read Vocation DB/import Vocation domain classes. Optional Conveyance delivery is domain-blind opaque protected transport and does not transfer authority.

Any future private cross-device command/write capability requires an explicit Vocation-owned authority/conflict/reconciliation design.

## 18. Packaging/development runtime

Production-style local start serves the built frontend through Vocation's local backend and may open the local Vocation URL explicitly at startup.

Development uses a Windows launcher that starts backend + Vite. The first manual acceptance exposed that the current launcher hides backend failures and may make stale child-process/native-file-lock diagnosis difficult. #52 owns targeted readiness/cleanup/diagnostic changes; it must never indiscriminately kill unrelated Python processes.

Orientation Embed Host is pinned as a static frontend artifact; explicit Place Search/geocoding uses configured Orientation backend. Orientation outage must fail the explicit geo action visibly while preserving existing/manual Vocation state.

## 19. Observability

- structured logs;
- Import/Prompt correlation/provenance identifiers;
- stable error codes;
- no unnecessary full private Clipboard/prompt/document content in logs;
- development startup should make backend readiness/failure visible (#52).

## 20. Contract testing

Repository gates cover as applicable:

- JSON Schema contracts/examples;
- Research/Update/Availability semantics;
- Prompt output/provenance;
- internal OpenAPI/TypeScript generation consistency;
- Published Opportunity Overview/Map Projection contracts;
- Orientation adapter/host bridge boundaries;
- migrations/repositories/domain/application services;
- frontend behavior;
- Windows production smoke.

Synthetic CI proves deterministic correctness but does not replace manual current-market/product acceptance.

## 21. Duplicate Case decisions

DuplicateDecision is append-only review history separate from DuplicateCase evidence. Current review state is derived from the latest decision.

`confirmed_duplicate` does not invoke a merge engine. No involved Opportunity/Posting identity, Assessment, Decision, Group, ApplicationCase, Document or Published reference is rewritten automatically.

## 22. Forbidden architecture shortcuts

Not allowed without a separately accepted architecture decision:

- shared database across contexts;
- direct cross-context Domain Class imports as integration;
- UI writes DB directly;
- parser decides merges;
- External Research mutates protected private state;
- Orientation/renderer decides Vocation WorkLocation/SearchArea/Precision/Fit/Availability/ExternalLink semantics;
- Vocation duplicates generic Place Search/geocoding/map rendering when Orientation satisfies the concrete use case;
- browser adapter chooses business-preferred Posting;
- Career/Profile document extraction silently mutates Candidate Profile;
- new microservice solely to organize source code or isolate one library;
- silent changes to frozen Research/Published contracts.

## 23. Product-acceptance relationship

The architecture above remains valid even though the first post-v0.4 manual product pass rejected major UI choices. #45–#50 should reshape presentation/workflows while preserving these ownership and provenance rules.

`docs/17_MANUAL_PRODUCT_ACCEPTANCE.md` is authoritative for the current release gate and which product concepts are implemented vs planned.
