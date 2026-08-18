# Vocation

Vocation is a standalone, local-first application for a personal job market. It turns externally researched job information into a structured, traceable and durable personal working set without making external research or automated application submission part of the application itself.

## Current status

Stable `main` remains the released **v0.4.0 standalone baseline**. The `dev` branch contains the completed post-v0.4 qualitative capability work from #31 and has passed the automated first-user acceptance path.

The first real local/manual product pass started on **2026-08-18** and exposed blocking UX and workflow findings. The automated acceptance therefore does **not** count as product acceptance and no next semantic version has been chosen. The current findings, product direction and release gate are documented in `docs/18_MANUAL_PRODUCT_ACCEPTANCE.md` and tracked by #42 with focused follow-up issues #45–#52.

The next release is considered only after the blocking findings are implemented or consciously deferred, the current-market workflow is repeated with real data, and the exact resulting release candidate passes the repository gates.

### Stable v0.4.0 baseline

Vocation v0.4.0 closes the released standalone baseline from research planning to application tracking:

- Vocation-owned assessment criteria and versioned research prompts;
- Research Bundle 1.0 initial imports and Research Update Bundle 2.0 scoped updates;
- structural and semantic validation, import reports, provenance and atomic persistence;
- deterministic Posting identity and explicit, append-only Duplicate Case review decisions;
- Opportunity list/detail, personal assessments, tracking status, exclusion/restore and decision history;
- evidence-derived Availability/Freshness with dedicated update prompting and import;
- Groups and Application Waves with ordered memberships;
- comparison of selected Opportunities without ranking or hidden scoring;
- Vocation-owned Work Locations, MapLocationResolution and Map Projection;
- generic geocoding and map rendering through Orientation rather than duplicated geo infrastructure;
- explicit External Link selection and browser opening only after user action;
- ApplicationCase lifecycle and revisioned private Application Materials;
- immutable private ApplicationDocument content with integrity checking, upload and explicit read-only open access;
- Published Opportunity Overview 1.0 and Published Map Projection 1.0 as frozen, client-neutral read contracts.

The v0.4.0 scope deliberately does **not** include automatic research through a paid LLM API, crawling, automatic application submission, e-mail/calendar automation, automatic duplicate merging, document editing/generation, or cross-device write synchronization. Those remain separate future decisions rather than unfinished v0.4.0 requirements.

### Implemented post-v0.4 capabilities on `dev`

The completed acceptance wave adds the qualitative personal-search layer without changing the frozen Research Bundle or Published contracts:

- a private, revisioned Candidate Profile separated from Vocation-owned search policy;
- multiple persistent Search Profiles with a selectable default and explicit evaluation policy;
- deterministic, explainable Opportunity Fit with weighted criterion contributions, evidence completeness and separate hard-constraint status;
- profile-aware, quality-first Initial Research prompts with exact profile/candidate provenance snapshots and linked Research Bundle 1.0 imports;
- an Opportunity workspace with text search, profile-aware filtering/sorting and private persistent notes that remain separate from imported evidence;
- the currently implemented navigation around **Stellenmarkt**, **Profil & Suche**, **Recherche** and **Organisation**, with manual implementation-oriented surfaces under **Werkzeuge**;
- a deterministic realistic first-user acceptance flow covering initial research, linked import, fit, personal state, scoped update, provenance preservation and application restart.

The currently implemented navigation and form layout are **not** the accepted final product design. Manual acceptance specifically identified the global next-step panel, dense Stellenmarkt controls, mixed terminology, raw multiline Search Profile fields and application/organisation presentation as blockers. See `docs/18_MANUAL_PRODUCT_ACCEPTANCE.md`.

### Accepted post-v0.4 product direction

Planned work now focuses on:

- a deliberate UI/information-architecture redesign with likely primary areas **Stellenmarkt**, **Profile**, **Recherche** and **Bewerbungen**;
- a durable personal career profile with reusable local CV/certificate/evidence documents;
- structured Search Profile controls, explicit place/radius search areas and maintainable role/technology/industry vocabularies;
- explicit research strategies such as company-first career-page research, regional/domain grinds and freshness re-checks;
- a coherent application workspace and explicitly reviewed prompt-assisted application-material drafts;
- a replaceable document-extraction boundary before any justified decision to split generic PDF/OCR understanding into another service.

These items are roadmap/acceptance work, not claims about the currently released v0.4.0 product.

## Ownership and system integration

Vocation is independently owned and locally authoritative for its job-market semantics and persistence. Wiiii Got This may consume explicit Published Vocation contracts but does not read the Vocation database or own Vocation business logic.

Generic geospatial capability belongs to Orientation. Vocation owns Work Location, Precision, MapLocationResolution, Map Projection and all job-market information/actions. `OrientationGeocoder` consumes Orientation Place Search, while the browser map uses the pinned Orientation Embed Host through `orientation.host-bridge` 1.0. If the optional Orientation backend is unavailable, geocoding fails visibly; existing local data and manual location resolution remain usable.

Search Profile search areas may use the same Orientation place-search boundary for generic place selection. Vocation still owns the job-search meaning of target areas, radii, remote/relocation policy and fit.

Published Opportunity Overview 1.0 is available at `/published/v1/opportunity-overview`. Published Map Projection 1.0 is available at `/published/v1/map-projection`. Both remain outside the internal React OpenAPI and are read-only provider-owned contracts.

## Technology stack

Python >=3.13 (development/tooling target 3.13), FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite and JSON Schema; React, TypeScript and Vite. Repository validation uses pytest, Ruff, mypy, Vitest, Testing Library and Biome. Internal frontend API types are generated from FastAPI OpenAPI.

## Local development

Prerequisites: Python >=3.13, [uv](https://docs.astral.sh/uv/), Node.js 22 and pnpm.

```powershell
uv sync --locked --extra dev
pnpm --dir frontend install --frozen-lockfile
.\scripts\dev.ps1
```

Run the complete repository check:

```powershell
.\scripts\check.ps1
```

For a production-style local start:

```powershell
pnpm --dir frontend build
.\.venv\Scripts\python -m vocation
```

The application starts on `127.0.0.1:8765` by default and opens the local browser unless `--no-browser` is supplied. Database migrations run automatically at application startup.

The current Windows development launcher starts the backend as a hidden child process and Vite in the foreground. Manual acceptance exposed weak backend-failure visibility and a possible stale-process/file-lock path; #52 tracks a targeted launcher fix.

The Orientation Embed Host is retained under `frontend/public/orientation-map/`; `ORIENTATION_SOURCE_SHA.txt` records the exact Orientation source revision used for the embedded artifact. Explicit geocoding uses `VOCATION_ORIENTATION_BASE_URL`, defaulting to `http://127.0.0.1:8080`.

## Local data and privacy

Development data defaults to `data/vocation.db` and `data/application-documents/`. Frozen/package-aware configuration uses `%LOCALAPPDATA%\Vocation`. `VOCATION_DATABASE_URL` and `VOCATION_DOCUMENT_STORE_DIR` can override these locations.

Local databases, imported job data, private application documents, generated personal prompts, logs, credentials and other private data must remain untracked. The repository `.gitignore` excludes the normal local data locations and database files.

## Deliberate future scope

The following are not required to consider the released v0.4.0 standalone baseline complete, but some are now explicit post-v0.4 product work:

- structured reusable personal profile documents and future extraction-assisted profile proposals (#46);
- structured Search Profile controls, search areas and reference catalogs (#47/#48);
- explicit research-strategy/coverage workflows (#49);
- application workspace and reviewed application-material generation (#50);
- document delete/retention, rich editing/rendering/export or encryption semantics beyond separately accepted work;
- fuzzy or heuristic automatic Opportunity identity merging;
- a Duplicate Case merge engine or canonical-survivor model;
- additional Published Vocation contracts without a concrete consumer;
- Conveyance/private cross-device transport or cross-device writes;
- authentication, cloud hosting or a Vocation-owned iOS application;
- Orientation routing unless a concrete Vocation use case requires it.

Future work must preserve Vocation domain ownership and follow the system-wide decisions in `wgt-system/architecture`.

## Repository structure

```text
backend/       FastAPI application, domain, migrations and tests
frontend/      React/TypeScript UI and Vitest tests
docs/          Product specification and ADRs
schemas/       Versioned import and Published contracts
examples/      Synthetic fixtures
prompts/       Prompt templates and output contracts
scripts/       Development and repository-check scripts
```

## Branch and release model

`dev` is the long-lived development branch. `main` contains stable, presentable, versioned milestone releases. Release branches are short-lived and are merged back into `dev` before the stable `dev` state is promoted to `main` and tagged.

## License

MIT; see [LICENSE](LICENSE).
