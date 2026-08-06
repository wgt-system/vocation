# Vocation

Vocation is a standalone, local-first application for a personal job market. Research happens externally (initially through ChatGPT): Vocation generates criteria-driven prompts, imports versioned JSON Research Bundles, validates them, and provides a traceable read model.

## Current status: v0.1.0 first milestone

The first usable Research Bundle workflow is implemented:

- Vocation-owned assessment criteria and active-criteria prompt snapshots
- file and paste import for the closed Research Bundle 1.0 contract
- structural and semantic validation with atomic persistence and import reports
- provenance, canonical idempotency, and duplicate-import detection
- opportunity list and detail views with postings, sources, observations, and external assessments
- local SQLite migrations and a FastAPI/React desktop-oriented application

Vocation does not call a paid LLM API, submit applications, or open external links automatically. It remains independently runnable without Wiiii Got This, Illumination, or a future map service.

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

Research is external and import is initially a desktop capability. Mobile/iOS usage is read-only. Update bundles, fuzzy identity resolution, personal assessments and decisions, groups/waves, availability/freshness, comparison, maps, crawling, authentication, cloud hosting, and external read contracts are explicitly outside v0.1.0.

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
