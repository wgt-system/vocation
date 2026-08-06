# Vocation

Vocation ist eine eigenständig ausführbare Anwendung zur strukturierten Sichtung, Verwaltung, Bewertung und räumlichen Darstellung eines persönlichen Stellenmarkts.

Die eigentliche Recherche findet zunächst außerhalb von Vocation statt, insbesondere in ChatGPT. Vocation stellt dafür standardisierte Prompt-Vorlagen bereit, importiert die daraus erzeugten versionierten JSON-Bundles, validiert sie und überführt sie in einen dauerhaften, nachvollziehbaren Datenbestand.

## Kernziele

- Stellenwissen dauerhaft und quellenbezogen erhalten
- Job Opportunity, Job Posting, Source und Observation sauber trennen
- externe Bewertungen und persönliche Entscheidungen auseinanderhalten
- historische Änderungen und Verfügbarkeit nachvollziehbar machen
- Stellen filtern, vergleichen und auf Karten darstellen
- Originalanzeigen aus Listen, Details und Karten-Pins im Browser öffnen
- wiederholbare Recherche durch vorbereitete Initial-, Update- und Teilbereichs-Prompts
- eigenständige Desktop-Nutzung ohne Wiiii Got This
- spätere read-only Integration in Wiiii Got This und iOS

## Projektstatus

Der erste nutzbare Meilenstein wird als lokaler FastAPI-Dienst mit React-Oberfläche umgesetzt. Vocation besitzt eine eigene SQLite-Datenbank und bleibt ohne andere Projekte startbar.

## Entwicklung starten

Voraussetzungen: Python 3.13 und pnpm.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[test]"
pnpm --dir frontend install
.\scripts\dev.ps1
```

Für einen produktionsnahen lokalen Start wird zuerst das Frontend gebaut und anschließend nur der Python-Dienst gestartet:

```powershell
pnpm --dir frontend build
.\.venv\Scripts\python -m vocation
```

## Dokumentationsreihenfolge

1. `docs/01_DOMAIN_VISION.md`
2. `docs/02_SCENARIOS.md`
3. `docs/03_UBIQUITOUS_LANGUAGE.md`
4. `docs/04_SUBDOMAINS.md`
5. `docs/05_DOMAIN_MODEL.md`
6. `docs/06_CONTEXT_MAP.md`
7. `docs/07_APPLICATION_DESIGN.md`
8. `docs/08_IMPORT_CONTRACT.md`
9. `docs/09_READ_MODELS.md`
10. `docs/10_ARCHITECTURE.md`
11. `docs/11_ACCEPTANCE_TESTS.md`
12. `docs/12_PROMPT_WORKFLOWS.md`
13. `docs/13_IMPLEMENTATION_PLAN.md`
14. `docs/14_REVIEW_CHECKLIST.md`

## Verzeichnisübersicht

```text
vocation/
├── README.md
├── AGENTS.md
├── docs/
│   ├── 01_DOMAIN_VISION.md
│   ├── 02_SCENARIOS.md
│   ├── 03_UBIQUITOUS_LANGUAGE.md
│   ├── 04_SUBDOMAINS.md
│   ├── 05_DOMAIN_MODEL.md
│   ├── 06_CONTEXT_MAP.md
│   ├── 07_APPLICATION_DESIGN.md
│   ├── 08_IMPORT_CONTRACT.md
│   ├── 09_READ_MODELS.md
│   ├── 10_ARCHITECTURE.md
│   ├── 11_ACCEPTANCE_TESTS.md
│   ├── 12_PROMPT_WORKFLOWS.md
│   ├── 13_IMPLEMENTATION_PLAN.md
│   └── adr/
├── schemas/
│   └── research-bundle-v1.schema.json
├── examples/
│   └── imports/
└── prompts/
```

## Implementierungsregel

Codex oder andere Agenten dürfen keine fachlichen Entscheidungen erfinden, die in den Spezifikationen offen oder ausgeschlossen sind. Unklare Punkte sind als Blocker zu melden oder in einem ADR zu dokumentieren.
