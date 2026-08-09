# AGENTS.md

## Produkt

Vocation ist eine eigenständig ausführbare, überwiegend lesende Desktop-Anwendung für einen persönlichen Stellenmarkt.

## Verbindlicher Technologie-Stack für Version 1

- Python 3.13, FastAPI, Pydantic, SQLAlchemy 2, Alembic, SQLite, jsonschema und pytest
- React, TypeScript, Vite, Vitest und React Testing Library
- FastAPI stellt im Produktionsmodus das gebaute Frontend bereit.
- Vocation startet als eigener lokaler Dienst und benötigt weder Wiiii Got This noch einen anderen fachlichen Kontext.
- Die Entscheidung ist in `docs/adr/0007-version-1-technology-stack.md` dokumentiert.

## Maßgebliche Quellen

- Produktvision: `docs/01_DOMAIN_VISION.md`
- Szenarien: `docs/02_SCENARIOS.md`
- Fachsprache: `docs/03_UBIQUITOUS_LANGUAGE.md`
- Subdomains: `docs/04_SUBDOMAINS.md`
- Domänenmodell: `docs/05_DOMAIN_MODEL.md`
- Context Map: `docs/06_CONTEXT_MAP.md`
- Anwendungsfälle: `docs/07_APPLICATION_DESIGN.md`
- Importvertrag: `docs/08_IMPORT_CONTRACT.md`
- Read Models: `docs/09_READ_MODELS.md`
- Architektur: `docs/10_ARCHITECTURE.md`
- Akzeptanztests: `docs/11_ACCEPTANCE_TESTS.md`
- Prompt-Workflows: `docs/12_PROMPT_WORKFLOWS.md`
- Implementierungsplan: `docs/13_IMPLEMENTATION_PLAN.md`
- Architekturentscheidungen: `docs/adr/`

## Verbindliche Regeln

1. Vocation bleibt ohne Wiiii Got This eigenständig ausführbar und nutzbar.
2. Recherche findet außerhalb von Vocation statt.
3. Vocation kann vorbereitete Prompts erzeugen und JSON-Bundles importieren.
4. Vocation ruft keine kostenpflichtige LLM-API auf.
5. Externe JSON-Modelle werden über eine Anticorruption Layer übersetzt.
6. Persönliche Assessments und Decisions dürfen durch Importe nicht überschrieben werden.
7. Job Opportunity, Job Posting, Source und Research Observation sind getrennte Konzepte.
8. Historische Informationen werden nicht stillschweigend gelöscht oder überschrieben.
9. Externe Links dürfen nur über explizite Nutzeraktionen im Standardbrowser geöffnet werden.
10. Cross-device Nutzung erfolgt zunächst read-only über client-neutrale Published Vocation Capabilities; Wiiii Got This kann sie auf Windows und iPhone darstellen.
11. Keine direkte Datenbanknutzung durch Wiiii Got This, Illumination oder einen späteren Map Service.
12. Öffentliche Verträge werden versioniert und durch Contract Tests geschützt.
13. Neue Architekturentscheidungen werden als ADR dokumentiert.
14. Keine spekulative Service-Zerlegung innerhalb des Vocation Context.
15. Keine automatische Bewerbungserstellung oder -versendung.
16. Vocation bleibt lokale Autorität; Wiiii Got This liest nie die Vocation-Datenbank und besitzt keine Vocation-Fachlogik.
17. Veröffentlichung ist optional und abgeleitet. Ein Relay/Storage bleibt domänenblind und ist kein neuer Bounded Context.

## Arbeitsweise für Codex

Vor einer Implementierung:

1. maßgebliche Dokumente lesen,
2. Widersprüche und Blocker nennen,
3. keine Produktentscheidung selbst erfinden,
4. einen vertikalen Implementierungsschnitt auswählen,
5. Akzeptanzkriterien und Tests benennen.

Nach einer Implementierung:

1. relevante Tests ausführen,
2. Dokumentationsabweichungen melden,
3. Domain- oder Vertragsänderungen dokumentieren,
4. keine stillen Schemaänderungen vornehmen.
