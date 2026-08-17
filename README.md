# Vocation

Vocation is a standalone, local-first application for a personal job market. It turns externally researched job information into a structured, traceable and durable personal working set without making external research or automated application submission part of the application itself.

## Current status: v0.4.0 complete standalone baseline

Vocation v0.4.0 closes the current standalone product scope. The implemented workflow covers the full path from research planning to application tracking:

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

The current scope deliberately does **not** include automatic research through a paid LLM API, crawling, automatic application submission, e-mail/calendar automation, automatic duplicate merging, document editing/generation, or cross-device write synchronization. Those are separate future decisions rather than unfinished v0.4.0 requirements.

## Ownership and system integration

Vocation is independently owned and locally authoritative for its job-market semantics and persistence. Wiiii Got This may consume explicit Published Vocation contracts but does not read the Vocation database or own Vocation business logic.

Generic geospatial capability belongs to Orientation. Vocation owns Work Location, Precision, MapLocationResolution, Map Projection and all job-market information/actions. `OrientationGeocoder` consumes Orientation Place Search, while the browser map uses the pinned Orientation Embed Host through `orientation.host-bridge` 1.0. If the optional Orientation backend is unavailable, geocoding fails visibly; existing local data and manual location resolution remain usable.

Published Opportunity Overview 1.0 is available at `/published/v1/opportunity-overview`. Published Map Projection 1.0 is available at `/published/v1/map-projection`. Both remain outside the internal React OpenAPI and are read-only provider-owned contracts.

## Technology stack

Python 3.13, FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite and JSON Schema; React, TypeScript and Vite. Repository validation uses pytest, Ruff, mypy, Vitest, Testing Library and Biome. Internal frontend API types are generated from FastAPI OpenAPI.

## Local development

Prerequisites: Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 22 and pnpm.

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

The Orientation Embed Host is retained under `frontend/public/orientation-map/`; `ORIENTATION_SOURCE_SHA.txt` records the exact Orientation source revision used for the embedded artifact. Explicit geocoding uses `VOCATION_ORIENTATION_BASE_URL`, defaulting to `http://127.0.0.1:8080`.

## Local data and privacy

Development data defaults to `data/vocation.db` and `data/application-documents/`. Frozen/package-aware configuration uses `%LOCALAPPDATA%\Vocation`. `VOCATION_DATABASE_URL` and `VOCATION_DOCUMENT_STORE_DIR` can override these locations.

Local databases, imported job data, private application documents, generated personal prompts, logs, credentials and other private data must remain untracked. The repository `.gitignore` excludes the normal local data locations and database files.

## Deliberate future scope

The following are not required to consider the v0.4.0 standalone baseline complete:

- fuzzy or heuristic automatic Opportunity identity merging;
- a Duplicate Case merge engine or canonical-survivor model;
- document delete/retention, editing, generation, preview/export or encryption semantics;
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
