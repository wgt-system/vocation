$ErrorActionPreference = "Stop"
uv run ruff check backend
uv run ruff format --check backend
uv run mypy
uv run pytest
pnpm --dir frontend lint
pnpm --dir frontend format:check
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
pnpm --dir frontend api:check
