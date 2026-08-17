from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"expected release marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("docs/01_DOMAIN_VISION.md"),
    "**Status:** Draft 0.2  \n",
    "**Status:** v0.4.0 complete standalone baseline  \n",
)
replace_once(
    Path("docs/13_IMPLEMENTATION_PLAN.md"),
    "**Status:** v0.3.0 released baseline; post-v0.3 development continues on `dev`.\n",
    "**Status:** v0.4.0 complete standalone baseline; Slices 1–18 implemented.\n",
)

index = Path("docs/INDEX.md")
text = index.read_text(encoding="utf-8")
row = "| 14_REVIEW_CHECKLIST | v0.4.0 Release-Review und Scope-Abschluss |"
if row not in text:
    marker = "| 13_IMPLEMENTATION_PLAN | vertikale Umsetzungsslices |"
    if marker not in text:
        raise SystemExit("implementation-plan index marker not found")
    text = text.replace(marker, f"{marker}\n{row}", 1)
    index.write_text(text, encoding="utf-8")
