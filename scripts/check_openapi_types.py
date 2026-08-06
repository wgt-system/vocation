from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from vocation.api.app import app  # noqa: E402


def main() -> None:
    api_dir = ROOT / "frontend" / "src" / "api"
    expected_spec = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    if (api_dir / "openapi.json").read_text(encoding="utf-8") != expected_spec:
        raise SystemExit("OpenAPI JSON is stale; run pnpm api:generate")
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "generated.ts"
        pnpm = "pnpm.cmd" if sys.platform == "win32" else "pnpm"
        subprocess.run([pnpm, "exec", "openapi-typescript", str(api_dir / "openapi.json"), "-o", str(output)], cwd=ROOT / "frontend", check=True)
        if output.read_text(encoding="utf-8") != (api_dir / "generated.ts").read_text(encoding="utf-8"):
            raise SystemExit("Generated API types are stale; run pnpm api:generate")


if __name__ == "__main__":
    main()
