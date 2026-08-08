# Vocation – Implementation Plan

**Status:** Draft 0.1

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

- bekannte IDs
- Update Scope
- Identity Resolver
- Duplicate Cases
- konservative Merge-Strategie

## Slice 8 – Availability und Freshness

- Availability Observations
- Evaluator
- Freshness
- UI Indicators

## Slice 9 – Groups und Waves

- Opportunity Groups
- Application Waves
- Filter und Übersicht

## Slice 10 – Karte

- Work Locations
- MapProjection
- Renderer
- Filterkonsistenz
- Pin Preview

## Slice 11 – External Links

- PreferredPostingSelector
- ExternalLinkPolicy
- Browser Adapter
- Quellenwahl im Pin und Detail

## Slice 12 – Vergleich

- Comparison Read Model
- UI

## Slice 13 – Mobile Read Contract

- versionierte Read API oder Snapshot
- read-only Contract Tests
- keine iOS-App in diesem Slice

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

Der v0.2.0-Scope umfasst versionierte Personal Assessments, Tracking Status, Decision History, Exclusion/Restore sowie Desktop-API- und React-Steuerung. Nicht enthalten bleiben Update-Bundles, fuzzy matching, Rankings, Gruppen/Waves, Maps, mobile Verträge, Crawling, kostenpflichtige LLM-APIs und Authentifizierung.
