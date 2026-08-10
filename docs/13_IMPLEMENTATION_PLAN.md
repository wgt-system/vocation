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

Slice 9 freezes Availability Check Bundle 1.0 and its evidence-derived semantics. Availability Prompt generation, the dedicated Availability Import HTTP boundary, internal Availability/Freshness read-model/API integration, list filters/badges, and detail/history UI are implemented on `dev`. This remains post-v0.3 development and does not change Published Opportunity Overview 1.0.

## Slice 10 – Groups und Waves (implementiert auf `dev`)

- Opportunity Groups
- Application Waves
- Filter und Übersicht

V1 definiert `OpportunityGroup` als Aggregate mit Type `general` oder `application_wave`; Application Wave ist kein separates Aggregate. Implementiert sind `CreateOpportunityGroup`, `EditOpportunityGroup`, `DeleteOpportunityGroup`, `AddOpportunityToGroup`, `RemoveOpportunityFromGroup` und `ReorderOpportunityGroup`, persistente geordnete Memberships, `/api/groups`, `group_id`-Filter, Opportunity List/Detail Memberships und die React Groups & Waves UI. Membership ist veränderbarer Organisationszustand; Gruppen verändern keine Opportunity-, Personal-, Research- oder Availability-Daten. Published Opportunity Overview 1.0 bleibt unverändert.

## Slice 11 – Karte (implementiert auf `dev`)

- Work Locations
- MapProjection
- Renderer
- Filterkonsistenz
- Pin Preview

V1 führt `MapLocationResolution` als Vocation-owned Supporting Data pro WorkLocation ein. Implementiert sind Persistence, explizite Manual-/Geocoder-Auflösung, provider-neutraler Geocoder-Port mit konfigurierbarem Nominatim-Adapter, expliziter Geocode-Endpunkt, interne MapProjection, `/api/map`, Leaflet/React Leaflet, gemeinsame List/Map-Filter über die aktuell sichtbaren Opportunity IDs, Marker-Popups mit Vocation-Details-Navigation sowie Geocode/Manual/Delete-UI mit OpenStreetMap-Tile-Attribution. Research Bundles bleiben unverändert; Resolution ist nicht append-only Evidence oder Decision History, überschreibt keine WorkLocation Precision und wird nur explizit durch den Nutzer ausgelöst. Keine automatische/background Geocodierung, kein Address Crawling, keine externe Browser-Navigation und keine Status-/Personal-/Research-/Availability-Mutation. Published Opportunity Overview 1.0 bleibt unverändert; Nominatim und Leaflet bleiben austauschbare Infrastruktur.

## Slice 12 – External Links (implementiert auf `dev`)

- PreferredPostingSelector
- ExternalLinkPolicy
- Browser Adapter
- Quellenwahl im Pin und Detail

V1 definiert ExternalLink als abgeleiteten Read-/Application-Wert ohne eigene Persistenz. Implementiert sind ExternalLinkPolicy, deterministischer PreferredPostingSelector, SQLAlchemy Read-Adapter, SystemBrowserAdapter, `/api/external-links`, typed interne OpenAPI-/Frontend-Clients, Opportunity-Detail-Workflow sowie Map-Popup-Navigation mit dedupliziertem Link-Laden pro Opportunity. Die Policy akzeptiert nur absolute HTTPS-URLs mit Host und prüft lokal ohne URL-Probing. Availability, Source Type, `observed_at` und Posting ID bestimmen das Ranking; explizite Auswahl wird nicht gespeichert. `OpenPostingInBrowser` ist ausschließlich Nutzeraktion. MapProjection bleibt URL-frei; Research Contracts und Published Opportunity Overview 1.0 bleiben unverändert.

## Slice 13 – Vergleich (Semantik eingefroren, Implementierung folgt)

- Comparison Read Model
- UI

V1 definiert `OpportunityComparisonView` als internen, read-only und nicht persistierten Vergleich für 2 bis 4 explizit geordnete, existierende Opportunities. Die Ansicht zeigt Summary, Availability-evidence Freshness, Groups/Waves, sechs Research-Dimensionen und Opportunity-scoped Assessments mit explizitem Missing-State und deterministischer Evidenzreihenfolge. Sie ist kein Ranking, Scoring, Recommendation, Winner Selector oder neue Assessment-Domäne. Es gibt keine inferred Contradictions, keine URLs/Browser-Aktionen und keine Mutation. Eine konkrete Risk-Read-Quelle ist nicht implementiert; Risk-Vergleich bleibt spätere Arbeit. Published Opportunity Overview 1.0 bleibt unverändert.

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

Issue #10 – scoped prompting und Desktop-Update-Workflow: abgeschlossen. Research Bundle `1.0` bleibt unverändert und initial-only. Vocation v0.3.0 enthält Research Update Bundle 2.0, scoped Full/Company/Opportunity/Gap Filling updates, Prompt Context Snapshots und opaque Correlation References, deterministische Posting-Identität, ungelöste Duplicate Cases ohne automatischen Merge, read-only Planning und atomaren Update Apply, PromptRun/ResearchImport-Traceability, den vollständigen Desktop Research Prompt preview/copy/save/import workflow sowie die implementierte Published Opportunity Overview 1.0 Publication auf `dev`. Issue #13 ist end-to-end implementiert: Availability Prompt generation, dedizierter Availability Import, Availability/Freshness Read Models/API sowie React/Desktop-Workflow mit Listenfiltern, Badges und Detail-/Historienansicht. Issue #14 Groups/Waves und Issue #15 Map sind end-to-end auf `dev` implementiert. Issue #16 External Links ist end-to-end auf `dev` implementiert; Research contracts und Published Opportunity Overview 1.0 bleiben unverändert. Comparison folgt danach.
