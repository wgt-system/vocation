# Vocation – Implementation Plan

**Status:** v0.3.0 released baseline.

## Phase 0 – Spezifikationsprüfung

Codex liest alle Dokumente und meldet:

- Widersprüche,
- Blocker,
- untestbare Kriterien,
- fehlende Vertragsdetails.

Noch kein Produktcode.

## Slice 1 – Projektgrundlage

- Repository-Struktur
- Build/Run
- Testumgebung
- lokale Datenbank und Migrationen
- Health Check
- Logging

## Slice 2 – Research Bundle Contract

- JSON Schema
- Parser
- Validation
- Fingerprint
- Beispieltests
- noch keine UI

## Slice 3 – Kernmodell Import

- Company
- Opportunity
- Posting
- Observation
- Import Record
- atomare Transaktion
- Contract- und Domain Tests

## Slice 4 – Job List und Detail

- Query Services
- erste Read Models
- Desktop UI
- Filter und Detailansicht

## Slice 5 – Assessments und Decisions

- External Assessment
- Personal Assessment
- Risks
- Tracking Status
- Exclusion/Restore
- History

## Slice 6 – Prompt Generation

- Prompt Templates
- Prompt Scope
- Context Snapshot
- Prompt Preview
- Clipboard
- Prompt Run History

## Slice 7 – Update Imports und Dubletten

- Vocation-issued opaque Correlation References
- gespeicherter Prompt Context und Update Scope
- deterministische Posting-Identität
- ungelöste Duplicate Cases als Evidenz
- kein automatischer Merge

## Post-v0.3 Priorität: Data Publication

### Slice 8 – Published Opportunity Overview 1.0

- Vocation-owned projection
- versioned client-neutral Published Contract
- contract tests
- local publication endpoint/artifact boundary
- transport-independent
- no iOS implementation in Vocation
- no remote relay implementation yet
- no personal-state write commands

Contract 1.0 is frozen in `schemas/published-opportunity-overview-v1.schema.json` with a canonical fictional example and schema-only contract tests. Slice 8 is implemented on `dev` with the local read-only boundary `/published/v1/opportunity-overview`; it remains outside the internal React OpenAPI. No relay, WGT client, authentication, remote persistence, or cross-device writes are implemented.

### Slice 9 – Availability und Freshness

- Availability Observations
- Evaluator
- Freshness
- UI Indicators

Slice 9 freezes Availability Check Bundle 1.0 and its evidence-derived semantics; this backend task implements persistence and import/evaluator foundations, while read-model/API/UI integration remains subsequent work.

## Slice 10 – Groups und Waves

- Opportunity Groups
- Application Waves
- Filter und Übersicht

## Slice 11 – Karte

- Work Locations
- MapProjection
- Renderer
- Filterkonsistenz
- Pin Preview

## Slice 12 – External Links

- PreferredPostingSelector
- ExternalLinkPolicy
- Browser Adapter
- Quellenwahl im Pin und Detail

## Slice 13 – Vergleich

- Comparison Read Model
- UI

## Slice 14 – Client-neutral Published Capability expansion

- weitere client-neutrale Published Vocation Capabilities
- read-only Contract Tests
- keine iOS-App in Vocation

## Luna-Parallelisierung

Geeignet:

- Schema und Beispiele
- Contract Tests
- UI-Komponenten mit stabilen Read Models
- Dokumentationsprüfung
- Browseradapter
- Map Renderer

Nicht parallelisieren, solange instabil:

- Opportunity Identity
- Merge-Regeln
- Importtransaktion
- Decision-Modell

## Done-Kriterien je Slice

- maßgebliche Dokumente genannt,
- Tests grün,
- keine stillen Vertragsänderungen,
- ADRs aktualisiert,
- Acceptance Tests nachvollziehbar erfüllt,
- eigenständiger Start bleibt möglich.
## v0.2.0 – Persönliche Triage

Der v0.2.0-Scope umfasst versionierte Personal Assessments, Tracking Status, Decision History, Exclusion/Restore sowie Desktop-API- und React-Steuerung. Nicht enthalten bleiben Update-Bundles, fuzzy matching, Rankings, Gruppen/Waves, Maps, Published Vocation Capabilities, Crawling, kostenpflichtige LLM-APIs und Authentifizierung.

## v0.3.0 – Implementierungsstand

Issue #7 – Research Update Bundle 2.0 Contract: abgeschlossen.

Issue #8 – deterministische Identität und ungelöste Duplicate Cases: abgeschlossen.

Issue #9 – Prompt Context Persistence, read-only Planning und atomarer Update Import: abgeschlossen.

Issue #10 – scoped prompting und Desktop-Update-Workflow: abgeschlossen. Research Bundle `1.0` bleibt unverändert und initial-only. Vocation v0.3.0 enthält Research Update Bundle 2.0, scoped Full/Company/Opportunity/Gap Filling updates, Prompt Context Snapshots und opaque Correlation References, deterministische Posting-Identität, ungelöste Duplicate Cases ohne automatischen Merge, read-only Planning und atomaren Update Apply, PromptRun/ResearchImport-Traceability, den vollständigen Desktop Research Prompt preview/copy/save/import workflow sowie die implementierte Published Opportunity Overview 1.0 Publication auf `dev`. Slice 9 ist als Contract Freeze abgeschlossen; Availability/Freshness-Implementierung und Read-Model-Integration sind noch in Arbeit. Groups/Waves, Maps, External Navigation und Comparison folgen danach.
