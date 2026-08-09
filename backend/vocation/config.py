from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", REPOSITORY_ROOT))


@dataclass(frozen=True)
class Settings:
    database_url: str
    frontend_dist: Path
    schema_path: Path
    update_schema_path: Path
    initial_prompt_path: Path
    output_contract_path: Path
    update_prompt_dir: Path


def get_settings() -> Settings:
    if getattr(sys, "frozen", False):
        data_dir = Path(os.getenv("LOCALAPPDATA", Path.home())) / "Vocation"
    else:
        data_dir = REPOSITORY_ROOT / "data"
    default_database = f"sqlite:///{(data_dir / 'vocation.db').as_posix()}"
    return Settings(
        database_url=os.getenv("VOCATION_DATABASE_URL", default_database),
        frontend_dist=RESOURCE_ROOT / "frontend" / "dist",
        schema_path=RESOURCE_ROOT / "schemas" / "research-bundle-v1.schema.json",
        update_schema_path=RESOURCE_ROOT / "schemas" / "research-update-bundle-v2.schema.json",
        initial_prompt_path=RESOURCE_ROOT / "prompts" / "initial-research.md",
        output_contract_path=RESOURCE_ROOT / "prompts" / "output-contract.md",
        update_prompt_dir=RESOURCE_ROOT / "prompts",
    )
