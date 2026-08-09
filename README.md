# Vocation

Vocation is a standalone, local-first application for a personal job market. Research happens externally (initially through ChatGPT): Vocation generates criteria-driven prompts, imports versioned JSON Research Bundles, validates them, and provides a traceable read model.

## Current status: v0.3.0 released baseline

The first usable Research Bundle workflow is implemented:

- Vocation-owned assessment criteria and active-criteria prompt snapshots
- file and paste import for the closed Research Bundle 1.0 contract
- structural and semantic validation with atomic persistence and import reports
- provenance, canonical idempotency, and duplicate-import detection
- opportunity list and detail views with postings, sources, observations, and external assessments
- local SQLite migrations and a FastAPI/React desktop-oriented application

The v0.2.0 personal triage baseline additionally includes immutable personal assessment revisions, tracking status, exclusion/restore decisions, decision history, and desktop triage controls. Vocation v0.3.0 is the controlled research-update release: Research Update Bundle 2.0, scoped Full/Company/Opportunity/Gap Filling updates, Prompt Context Snapshots and opaque Correlation References, deterministic Posting identity, unresolved Duplicate Cases without automatic merge, read-only planning and atomic Update apply, PromptRun/ResearchImport traceability, and the complete desktop Research Prompt preview/copy/save/import workflow. Initial Research Bundle 1.0 compatibility is retained.

Vocation does not call a paid LLM API, submit applications, or open external links automatically. It remains independently runnable without Wiiii Got This, Illumination, or a future map service. Wiiii Got This is the primary cross-device presentation for suitable published Vocation capabilities on Windows and iPhone; Vocation remains the local authority.

The post-v0.3 Availability/Freshness slice is implemented on `dev`: controlled Availability Check prompting and import, append-only evidence-derived Posting/Opportunity Availability and availability-evidence Freshness, list filters/badges, and detail/history views. Groups/Waves are also implemented on `dev`: persistent typed groups, ordered memberships, CRUD, filtering, and the React Groups & Waves workflow. Both remain outside the released v0.3.0 baseline.

Published Opportunity Overview 1.0 is implemented on `dev`. Its canonical contract remains `schemas/published-opportunity-overview-v1.schema.json`; the local read-only endpoint is `/published/v1/opportunity-overview` and remains outside the internal React OpenAPI. No relay, WGT client, authentication, remote persistence, or cross-device writes are implemented.

## Technology stack

Python 3.13, FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite, JSON Schema, pytest, Ruff, and mypy; React, TypeScript, Vite, Vitest, Testing Library, Biome, and pnpm. API types are generated from the FastAPI OpenAPI contract.

## Local development

Prerequisites: Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 22, and pnpm.

```powershell
uv sync --locked --extra dev
pnpm --dir frontend install --frozen-lockfile
.\scripts\dev.ps1
```

Run the complete repository check (the same checks used by CI):

```powershell
.\scripts\check.ps1
```

For a production-style local start:

```powershell
pnpm --dir frontend build
.\.venv\Scripts\python -m vocation
```

The application uses local SQLite data. Local databases, imported job data, generated personal prompts, logs, credentials, and other private data must remain untracked.

## Boundaries and limitations

Research is external and import is initially a desktop capability. Cross-device use is read-only publication consumed by Wiiii Got This and is optional; local-only operation remains supported. Fuzzy identity resolution, comparison, maps, crawling, authentication, and cloud hosting remain outside v0.3. Availability/Freshness and Groups/Waves are post-v0.3 development implemented on `dev`; Published Opportunity Overview 1.0 remains unchanged and contains neither capability. Published Opportunity Overview 1.0 is implemented locally, without relay, WGT client, authentication, remote persistence, or cross-device writes.

## Repository structure

```text
backend/       FastAPI application, domain, migrations, and tests
frontend/      React/TypeScript UI and Vitest tests
docs/          Product specification and ADRs
schemas/       Versioned import contracts
examples/      Synthetic import fixtures
prompts/       Prompt templates and output contract
scripts/       Development and complete-check scripts
```

## Branch and release model

`dev` is the long-lived development branch. Normal work happens there; feature branches are optional for parallel or risky experiments. `main` contains stable, presentable, versioned milestone releases only. Completed milestones are merged from `dev` into `main` and tagged (for example `v0.1.0`).

## License

MIT; see [LICENSE](LICENSE).
