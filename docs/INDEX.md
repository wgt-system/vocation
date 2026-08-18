# Dokumentationsindex

| Datei | Zweck |
|---|---|
| 01_DOMAIN_VISION | Produktziel, Grenzen, Erfolg und stabiler v0.4.0-Fachrahmen |
| 02_SCENARIOS | reale und kritische Nutzungsszenarien |
| 03_UBIQUITOUS_LANGUAGE | verbindliche Fachsprache und Trennung von Domain- und UI-Begriffen |
| 04_SUBDOMAINS | Core, Supporting, Generic |
| 05_DOMAIN_MODEL | Aggregates, Entities, Services und Regeln |
| 06_CONTEXT_MAP | Kontextgrenzen und Beziehungen |
| 07_APPLICATION_DESIGN | Commands, Queries, Use Cases und UI-Flows |
| 08_IMPORT_CONTRACT | Research-/Update-/Availability-Verträge und Importgrenzen |
| 09_READ_MODELS | interne/private/published Read Models und Projection-Grenzen |
| 10_ARCHITECTURE | technische Struktur, Ownership und Integrationsgrenzen |
| 11_ACCEPTANCE_TESTS | dauerhafte automatisierte und manuelle Acceptance-Kriterien |
| 12_PROMPT_WORKFLOWS | versionierte externe Recherche-, Update- und Availability-Prompts |
| 13_IMPLEMENTATION_PLAN | abgeschlossene Slices, implementierter dev-Stand und aktueller Produkt-Roadmap |
| 14_REVIEW_CHECKLIST | historischer v0.4.0 Release-Review und Scope-Abschluss |
| 15_PERSONAL_SEARCH_CONTEXT | privates Candidate Profile, Search Profiles, Provenienz und aktuelle Produktgrenzen |
| 16_OPPORTUNITY_FIT | Search-Profile-Evaluationspolitik und erklärbarer Opportunity Fit |
| 17_MANUAL_PRODUCT_ACCEPTANCE | Ergebnis der ersten manuellen Produktabnahme, Blocker und akzeptierte Post-v0.4-Produkt-Richtung |
| 18_FIRST_USER_ACCEPTANCE | deterministischer First-User-Flow und manueller Current-Market-Acceptance-Check |

## Statushinweis

`main` bleibt der stabile v0.4.0-Stand. Die automatisierte Post-v0.4-Acceptance auf `dev` ist technisch grün, die erste manuelle Produktabnahme vom 2026-08-18 hat jedoch blockierende UX- und Workflow-Funde ergeben. Der aktuelle Entscheidungs- und Release-Gate-Stand ist in `17_MANUAL_PRODUCT_ACCEPTANCE.md` dokumentiert; die Wiederholungsprozedur steht in `18_FIRST_USER_ACCEPTANCE.md`.

Historische ADRs/Release-Entscheidungen werden nicht rückwirkend auf neue Produktpläne umgeschrieben. Dieses nummerierte Set beschreibt die aktuelle Vocation-Seite der Architektur und Produktarbeit; systemweite Ownership bleibt in `wgt-system/architecture` autoritativ.
