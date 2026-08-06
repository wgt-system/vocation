from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database_url: str
    frontend_dist: Path
    schema_path: Path
    initial_prompt_path: Path
    output_contract_path: Path


def get_settings() -> Settings:
    data_dir = REPOSITORY_ROOT / "data"
    default_database = f"sqlite:///{(data_dir / 'vocation.db').as_posix()}"
    return Settings(
        database_url=os.getenv("VOCATION_DATABASE_URL", default_database),
        frontend_dist=REPOSITORY_ROOT / "frontend" / "dist",
        schema_path=REPOSITORY_ROOT / "schemas" / "research-bundle-v1.schema.json",
        initial_prompt_path=REPOSITORY_ROOT / "prompts" / "initial-research.md",
        output_contract_path=REPOSITORY_ROOT / "prompts" / "output-contract.md",
    )
