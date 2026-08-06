from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from vocation.api.app import app  # noqa: E402


def main() -> None:
    api_dir = ROOT / "frontend" / "src" / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    spec = api_dir / "openapi.json"
    spec.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pnpm = "pnpm.cmd" if sys.platform == "win32" else "pnpm"
    subprocess.run([pnpm, "exec", "openapi-typescript", str(spec), "-o", str(api_dir / "generated.ts")], cwd=ROOT / "frontend", check=True)


if __name__ == "__main__":
    main()
