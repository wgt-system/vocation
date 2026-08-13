# Vocation – Architecture

**Status:** Version 1 beschlossen

## 1. Architekturziele

- eigenständig startbare Desktop-Anwendung,
- klare Domain/Application/Infrastructure-Grenzen,
- keine Abhängigkeit von Wiiii Got This,
- versionierte Import- und Read Contracts,
- read-heavy Nutzung,
- lokale Datenhoheit,
- client-neutrale Published Read Projections für Wiiii Got This auf Windows und iPhone,
- geringe Betriebs- und Wartungskosten.

## 2. Laufzeitbild Version 1

```text
Desktop UI
   │
Application Layer
   │
Domain Model
   │
Repositories / Query Services
   │
Local Database
```

Zusätzliche Adapter:

- File Picker
- Clipboard
- Browser Launcher
- Map Renderer
- optional Geocoder

Vocation kann intern einen lokalen HTTP-Server verwenden, muss aber als ein eigenständig startbares Produkt erscheinen.

## 3. Technologieentscheidung Version 1

ADR-0007 legt verbindlich fest:

- Backend/Application: Python 3.13, FastAPI und Pydantic
- Persistenz: SQLAlchemy 2, Alembic und SQLite
- Vertragsvalidierung: JSON Schema Draft 2020-12 mit `jsonschema`
- Backend-Tests: pytest
- Frontend: React, TypeScript und Vite
- Frontend-Tests: Vitest und React Testing Library
- spätere Karte: Leaflet und OpenStreetMap

FastAPI stellt im Produktionsmodus die gebauten Frontend-Dateien bereit. Ein Python-Startvorgang startet den lokalen HTTP-Dienst und darf anschließend die lokale Vocation-URL über den Standardbrowser öffnen. Frontend und Backend müssen in der Produktion nicht separat gestartet werden.

Die Anwendung wird so strukturiert, dass eine spätere lokale Distribution mit PyInstaller möglich bleibt. Docker, Cloud-Infrastruktur und externe fachliche Laufzeitabhängigkeiten sind nicht Teil von Version 1.

## 4. Schichten

### Domain

- Entities, Value Objects, Aggregates
- Domain Services
- Domain Events
- keine Frameworkabhängigkeiten

### Application

- Commands und Queries
- Use-Case-Orchestrierung
- Transaktionen
- Berechtigungen und Plattform-Capability-Prüfung

### Infrastructure

- Datenbank
- JSON
- Files
- Clipboard
- Browser
- Map
- Logging

### Presentation

- Desktop UI
- internes HTTP API bleibt eine Presentation API und ist kein automatischer Published WGT Contract
- Vocation-owned Publication Adapter für client-neutrale Published Capabilities

## 5. Datenhaltung

Vocation besitzt seine eigene Datenbank.

Keine anderen Kontexte greifen direkt darauf zu.

Empfohlene Eigenschaften:

- Migrationen
- Transaktionen
- Backups/Export
- stabile interne IDs
- keine direkte Persistenz von UI-Read-Models als Wahrheit
- Rohbundle optional als Audit-Artefakt

Die initiale SQLite-Struktur wird ausschließlich durch Alembic-Migrationen erzeugt.

## 6. Prompt-Dateien

Prompt Templates liegen versioniert unter `prompts/`.

Die Runtime darf Templates laden und mit einem Prompt Context Snapshot rendern.

Prompt Templates enthalten keine geheimen oder benutzerspezifischen Daten außerhalb des expliziten Scopes.

Update-Prompt-Traceability folgt `PromptRun → PromptContextSnapshot ← ResearchImport`. Ein Update PromptRun gehört genau zu einem Snapshot; dessen opaque Correlation References sind snapshot-lokal. `ResearchImport` referenziert nicht direkt einen PromptRun. Initial Research liegt außerhalb dieser Update-Prompt-Context-Beziehung.

## 7. Import Pipeline

```text
File/Clipboard
→ Parse
→ Explicit 1.0/2.0 Dispatch
→ Schema/Contract Validate
→ Prompt Context and Scope
→ Identity
→ Deterministic Plan
→ Blocker Check
→ Single Atomic Apply
→ Import Report
```

Research Bundle `1.0` und Research Update Bundle `2.0` werden explizit getrennt dispatcht. Beim Update folgen nach Schema-/Contract-Validierung Prompt Context und Scope/Correlation-Prüfung, Identity, deterministischer Plan und Blocker-Prüfung; erst danach wird eine einzige atomare Apply-Transaktion ausgeführt. Merge-Entscheidungen gehören weder in Parsing noch in Persistenz. Strukturelle oder semantische Blocker verhindern jede fachliche Änderung. Partielle Imports sind nicht erlaubt.

## 8. Map Architecture

Version 1 darf eine lokale Kartenbibliothek verwenden.

Trennung:

- Vocation erzeugt MapProjection.
- Renderer zeichnet Features.
- Browserlinks werden über Application Command geöffnet.
- später kann dieselbe Projection an einen Shared Map Context geliefert werden.

## 9. External Browser Navigation

Technischer Adapter:

```text
ExternalLinkPolicy
→ OperatingSystemBrowserLauncher
```

Sicherheitsregeln:

- nur erlaubte Schemes,
- explizite Nutzeraktion,
- keine eingebettete Code-Ausführung,
- Fehler sichtbar,
- kein automatisches Öffnen während Import oder Kartenrendering.

## 10. Cross-device Publication

Vocation veröffentlicht versionierte, client-neutrale Published Vocation Capabilities.

Die Feldstruktur von `Opportunity Overview` 1.0 ist jetzt durch `schemas/published-opportunity-overview-v1.schema.json` kanonisch eingefroren. Der implementierte lokale Veröffentlichungspfad ist `/published/v1/opportunity-overview`; er bleibt außerhalb der internen React OpenAPI, während das bestehende `/api/...` React API interne Presentation API bleibt. HTTP/OpenAPI ist nicht die Quelle der Cross-Context-Payload.

`Published Map Projection` 1.0 ist als zweiter client-neutraler, transport-unabhängiger Published Contract durch `schemas/published-map-projection-v1.schema.json` eingefroren und unter `GET /published/v1/map-projection` implementiert. Ein dedizierter read-only Publication Repository/Service liest ausschließlich bereits vorhandene MapLocationResolutions. Publication geocodiert, mutiert oder resolved nichts; Features werden deterministisch nach Company Name, Opportunity Title, WorkLocation Label (jeweils case-insensitive) und `feature_ref` geordnet. Der Contract bleibt außerhalb der internen React OpenAPI, URL-frei und enthält weder persönliche, Research-, Availability-, Gruppen- noch Providerdaten. Published Opportunity Overview 1.0 bleibt unverändert.

ApplicationCases und private ApplicationMaterial-Metadaten gehören zur Vocation-Domain. Sie werden niemals durch Research/Availability oder Groups/Waves erzeugt und nicht über öffentliche Publication Endpoints ausgegeben. Eine spätere WGT-/Conveyance-Anbindung darf nur über eine separate private Grenze und opaque protected payloads erfolgen; Conveyance besitzt keine Vocation-Semantik.

Publication umfasst einen Vocation-eigenen Adapter und eine optionale Publication Snapshot/Metadata-Schicht. Ein Relay/Storage darf später als domänenblinde Infrastruktur ergänzt werden, ohne den Published Contract zu ändern.

Publication Age ist nicht Vocation Freshness: ein alter Snapshot bedeutet weder stale noch unavailable Job Postings.

Cross-device Reads müssen mit der letzten Published Projection funktionieren, wenn der Windows-PC ausgeschaltet ist. Local-only-Nutzung ohne konfigurierte Remote-Publikation bleibt vollständig unterstützt. Ein Sync Bounded Context wird nicht eingeführt; Cross-device Writes bleiben unentschieden.

WGT liest nie die Vocation-Datenbank, importiert keine Vocation-Domainklassen und führt keine Vocation-Fachlogik aus. Python/FastAPI läuft nicht im iPhone-WGT-Client.

## 11. Packaging

Desktop-Version soll mit einem einfachen Startvorgang ausgeliefert werden. Separate manuelle Starts von Frontend und Backend sind für den Nutzer nicht das Ziel.

Für die Entwicklung existiert ein Windows-Startskript. Im Produktionsmodus wird das mit Vite gebaute Frontend durch FastAPI ausgeliefert. Die Browseröffnung beim Anwendungsstart betrifft ausschließlich die lokale Vocation-URL; Import oder Darstellung fachlicher Daten öffnen niemals externe Links.

## 12. Observability

- strukturierte Logs
- Import Correlation ID
- Prompt Run ID
- Fehlercodes
- keine unnötige Speicherung kompletter sensibler Clipboard-Inhalte in Logs

## 13. Contract Testing

- JSON Schema Tests
- Beispielbundle-Tests
- Read Contract Snapshot Tests
- MapProjection Contract Tests
- Prompt Output Contract Tests
- Published Opportunity Overview 1.0 Contract Tests

## 14. Architekturgrenzen

Nicht erlaubt:

- Shared Database,
- direkte Cross-Context Imports von Domain Classes,
- UI schreibt direkt in Datenbank,
- Importparser enthält Merge-Entscheidungslogik,
- Map-Renderer entscheidet Work Location,
- Browseradapter wählt Preferred Posting.
