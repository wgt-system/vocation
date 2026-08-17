# Vocation – Architecture

**Status:** Version 1 beschlossen

## 1. Architekturziele

- eigenständig startbare Desktop-Anwendung,
- klare Domain/Application/Infrastructure-Grenzen,
- keine Abhängigkeit von Wiiii Got This für Vocation-Fachsemantik oder Persistenz,
- versionierte Import- und Read Contracts,
- read-heavy Nutzung,
- lokale Datenhoheit,
- client-neutrale Published Read Projections für Wiiii Got This auf Windows und iPhone,
- Wiederverwendung akzeptierter systemweiter generischer Capabilities statt eigener Duplikate,
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

Zusätzliche Adapter/Grenzen:

- File Picker
- Clipboard
- Browser Launcher
- Orientation Host Bridge für generisches Map Rendering
- OrientationGeocoder für explizite Geocodierung

Vocation kann intern einen lokalen HTTP-Server verwenden, muss aber als ein eigenständig nutzbares Vocation-Produkt erscheinen. Fachliche Autorität und lokale Persistenz bleiben in Vocation. Generic geospatial capability ist systemweit Orientation zugeordnet und wird über explizite Grenzen konsumiert.

## 3. Technologieentscheidung Version 1

ADR-0007 legt für die Vocation-eigene Runtime verbindlich fest:

- Backend/Application: Python 3.13, FastAPI und Pydantic
- Persistenz: SQLAlchemy 2, Alembic und SQLite
- Vertragsvalidierung: JSON Schema Draft 2020-12 mit `jsonschema`
- Backend-Tests: pytest
- Frontend: React, TypeScript und Vite
- Frontend-Tests: Vitest und React Testing Library

FastAPI stellt im Produktionsmodus die gebauten Frontend-Dateien bereit. Ein Python-Startvorgang startet den lokalen HTTP-Dienst und darf anschließend die lokale Vocation-URL über den Standardbrowser öffnen. Frontend und Backend müssen in der Produktion nicht separat gestartet werden.

Die generische Karte ist nach der systemweiten Orientation-Ownership-Entscheidung keine Vocation-Technologieentscheidung mehr. Vocation bündelt einen gepinnten Orientation Embed Host und adaptiert Vocation-owned MapProjection-Daten über `orientation.host-bridge` 1.0. Explizite Geocodierung nutzt einen Vocation-Application-Port mit `OrientationGeocoder` als Infrastrukturadapter gegen die konfigurierte Orientation-Backend-Grenze. Vocation kennt weder MapLibre- noch Photon-Semantik als eigene Domain-/Application-Semantik.

Die Anwendung wird so strukturiert, dass eine spätere lokale Distribution mit PyInstaller möglich bleibt. Docker, Cloud-Infrastruktur und externe fachliche Datenautorität sind nicht Teil von Version 1. Die konkrete lokale/remote Topologie einer konsumierten Orientation-Capability bleibt eine Deployment-Frage und transferiert keine Vocation-Fachsemantik.

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
- generische Ports wie `Geocoder`, ohne Orientation-/Provider-DTOs in der Domain

### Infrastructure

- Datenbank
- JSON
- Files
- Clipboard
- Browser
- Orientation-Adapter
- Logging

### Presentation

- Desktop UI
- internes HTTP API bleibt eine Presentation API und ist kein automatischer Published WGT Contract
- Vocation-owned Publication Adapter für client-neutrale Published Capabilities
- Vocation-to-Orientation Scene Adapter/Host für die lokale Kartenansicht

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

Die generische Geospatial-Capability ist systemweit Orientation zugeordnet. Die implementierte Trennung lautet:

- Vocation besitzt Work Location, Precision, `MapLocationResolution`, interne `MapProjection`, Opportunity-/Company-/Availability-/External-Link-Semantik und alle fachlichen Actions.
- Der Vocation-Application-Layer besitzt den provider-neutralen `Geocoder`-Port.
- `OrientationGeocoder` konsumiert `GET /api/v1/places/search` und übersetzt genau das benötigte generische Resultat in den Vocation-Application-Wert `GeocodingResult`.
- `OrientationMapFrame` adaptiert Vocation-owned Features, Informationen und Action References in eine Orientation Spatial Scene.
- Der gepinnte Orientation Embed Host rendert die Szene über `orientation.host-bridge` 1.0.
- Bridge-Aktionen werden an Vocation zurückgegeben; Vocation navigiert zu Details oder führt External-Link-Commands aus.

Damit entscheidet der Renderer weder Work Location/Precision noch Preferred Posting, Availability oder Tracking Status. Orientation liest keine Vocation-Datenbank und erhält keine Vocation-Domainklassen.

Die geschlossene `Published Map Projection 1.0` bleibt ein separater, Vocation-owned, URL-freier Published Contract und wird durch die lokale Orientation-Komposition nicht verändert. Eine spätere reichhaltige Cross-Context-Map-Publication muss als versionierter Nachfolger eingeführt werden statt Contract 1.0 still zu erweitern.

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

Orientation-Map-Actions sind nur Host-Events. Die eigentliche Auswahl und Ausführung externer Vocation-Links bleibt hinter `ExternalLinkPolicy` und dem Vocation Browser Adapter.

## 10. Cross-device Publication

Vocation veröffentlicht versionierte, client-neutrale Published Vocation Capabilities.

Die Feldstruktur von `Opportunity Overview` 1.0 ist jetzt durch `schemas/published-opportunity-overview-v1.schema.json` kanonisch eingefroren. Der implementierte lokale Veröffentlichungspfad ist `/published/v1/opportunity-overview`; er bleibt außerhalb der internen React OpenAPI, während das bestehende `/api/...` React API interne Presentation API bleibt. HTTP/OpenAPI ist nicht die Quelle der Cross-Context-Payload.

`Published Map Projection` 1.0 ist als zweiter client-neutraler, transport-unabhängiger Published Contract durch `schemas/published-map-projection-v1.schema.json` eingefroren und unter `GET /published/v1/map-projection` implementiert. Ein dedizierter read-only Publication Repository/Service liest ausschließlich bereits vorhandene MapLocationResolutions. Publication geocodiert, mutiert oder resolved nichts; Features werden deterministisch nach Company Name, Opportunity Title, WorkLocation Label (jeweils case-insensitive) und `feature_ref` geordnet. Der Contract bleibt außerhalb der internen React OpenAPI, URL-frei und enthält weder persönliche, Research-, Availability-, Gruppen- noch Providerdaten. Published Opportunity Overview 1.0 bleibt unverändert.

ApplicationCases und private ApplicationMaterial-Metadaten gehören zur Vocation-Domain. Sie werden niemals durch Research/Availability oder Groups/Waves erzeugt und nicht über öffentliche Publication Endpoints ausgegeben. Eine spätere WGT-/Conveyance-Anbindung darf nur über eine separate private Grenze und opaque protected payloads erfolgen; Conveyance besitzt keine Vocation-Semantik.

Die implementierte lokale ApplicationCase-Kette lautet: ApplicationCase-Domain → ApplicationCaseService → `SqlAlchemyApplicationCaseRepository` → SQLite/Alembic `0011` → internes FastAPI `/api/...` → typed React client → Opportunity-Detail-ApplicationCase-Panel. Persistiert werden `application_cases`, `application_case_lifecycle_events`, `application_materials` und `application_material_revisions`. Ein partieller Unique Index erzwingt höchstens einen nonterminalen Case je Opportunity. Lifecycle- und Material-Revision-Historie sind append-only; terminale Cases bleiben historisch. Opportunity Tracking Status bleibt unabhängig; es gibt keine automatische Import-, Group- oder Status-Kopplung.

Slice 16 trennt semantische Ownership von physischer Dokumentablage. Implementiert ist die Kette: ApplicationDocument-Domain → Alembic `0012` Metadata-Persistence in `application_documents` → `ApplicationDocumentStore`-Port → `FilesystemApplicationDocumentStore` → SQLAlchemy Repository → ApplicationDocumentService → private interne FastAPI-Endpunkte → typed Frontend Client → ApplicationCasePanel Upload-Workflow. Persistiert werden Metadata plus opaque `storage_ref`; Payload bytes liegen nicht in relationalen Tabellen. Der Composite FK `(material_id, material_revision)` verweist auf `application_material_revisions(material_id, revision)`; `UNIQUE(material_id, material_revision)` erzwingt ein Dokument pro Revision. Writes sind create-only und atomic, nutzen keinen rohen Storage Reference oder Original-Dateinamen als Pfad und besitzen keine Delete-Operation. Physische Details bleiben Infrastruktur und nicht Domainsemantik.

Document Reads validieren die Backing-Payload; fehlende oder korrupte Bytes sind explizite Integrity Errors. Slice 17 ist implementiert: Der ApplicationCasePanel bietet bei einem angehängten Dokument der exakt aktuellen Material-Revision die explizite `Öffnen`-Aktion über `GET /api/application-documents/{document_id}/content`; der Browser erhält den exakt geladenen `document.id` in einem neuen Kontext mit `noopener`/`noreferrer`. PDF, `text/plain` und `text/markdown` nutzen dieselbe private Grenze. ApplicationCase-Lifecycle bleibt unabhängig und löscht keine historischen Dokumente automatisch. Dokumente werden weder publiziert noch in Research/Availability/Prompt Contexts aufgenommen. Alle künftigen Cross-Context- oder privaten Integrationen folgen der autoritativen `wgt-system/architecture`; Vocation friert dafür keine zusätzliche Systempolitik ein.

Publication umfasst einen Vocation-eigenen Adapter und eine optionale Publication Snapshot/Metadata-Schicht. Für dauerhafte opaque Cross-Device-Zustellung kann WGT die Vocation-owned Projection schützen und über Conveyance transportieren; der Published Contract bleibt unverändert, Conveyance bleibt domänenblind und Vocation baut keinen eigenen Relay-/Storage-Stack.

Publication Age ist nicht Vocation Freshness: ein alter Snapshot bedeutet weder stale noch unavailable Job Postings.

Cross-device Reads müssen mit der letzten Published Projection funktionieren, wenn der Windows-PC ausgeschaltet ist. Local-only-Nutzung ohne konfigurierte Remote-Publikation bleibt vollständig unterstützt. Conveyance ist der separate akzeptierte generische Delivery-Bounded-Context; Vocation führt keinen eigenen Sync-Bounded-Context für Vocation-Semantik ein. Cross-device Writes bleiben unentschieden und benötigen ausdrücklich Vocation-owned Command-, Authority-, Merge-, Conflict- und Reconciliation-Semantik.

WGT liest nie die Vocation-Datenbank, importiert keine Vocation-Domainklassen und führt keine Vocation-Fachlogik aus. Python/FastAPI läuft nicht im iPhone-WGT-Client.

## 11. Packaging

Desktop-Version soll mit einem einfachen Startvorgang ausgeliefert werden. Separate manuelle Starts von Vocation-Frontend und Vocation-Backend sind für den Nutzer nicht das Ziel.

Für die Entwicklung existiert ein Windows-Startskript. Im Produktionsmodus wird das mit Vite gebaute Frontend durch FastAPI ausgeliefert. Die Browseröffnung beim Anwendungsstart betrifft ausschließlich die lokale Vocation-URL; Import oder Darstellung fachlicher Daten öffnen niemals externe Links.

Der Orientation Embed Host ist als statisches, auf eine konkrete Orientation-Source-SHA gepinntes Artefakt im Vocation-Frontend enthalten. Geocoding ist dagegen eine explizite Runtime-Integration mit dem konfigurierten Orientation Backend (`VOCATION_ORIENTATION_BASE_URL`, Default `http://127.0.0.1:8080`). Ist diese Capability nicht verfügbar, schlägt die explizite Geocode-Aktion sichtbar fehl; Vocation-Fachdaten, manuelle Resolution und bereits persistierte MapLocationResolutions bleiben lokal nutzbar.

Eine spätere Distribution kann Orientation-Capabilities lokal hosten oder anders topologisch bereitstellen. Diese Packaging-Entscheidung ändert weder die Bounded-Context-Ownership noch berechtigt Vocation, generisches Geocoding/Rendering erneut selbst zu implementieren.

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
- Orientation-Adapter-/Host-Bridge-Integrationstests an den Vocation-Grenzen

## 14. Architekturgrenzen

Nicht erlaubt:

- Shared Database,
- direkte Cross-Context Imports von Domain Classes,
- UI schreibt direkt in Datenbank,
- Importparser enthält Merge-Entscheidungslogik,
- Orientation/Map-Renderer entscheidet Vocation Work Location oder Precision,
- Vocation implementiert konkurrierendes generisches Geocoding/Map Rendering, wenn Orientation die benötigte Capability bereitstellt,
- Browseradapter oder Orientation wählt Preferred Posting.

## 15. Duplicate Case Resolution

Slice 18 ergänzt die bestehende DuplicateCase-Evidence um eine getrennte append-only `DuplicateDecision`-Historie. Alembic `0013` persistiert Entscheidungen mit einer eindeutigen monotonen Sequence pro Case und geschlossenem Outcome-Vokabular. Domain/Application leiten aktuelle Review-Sicht ausschließlich aus der letzten Decision ab; bestehende DuplicateCase-Evidence bleibt unverändert.

Die interne Kette lautet: `DuplicateCaseService` → `SqlAlchemyDuplicateCaseRepository` → `duplicate_case_decisions` → interne `/api/duplicate-cases`-Read-/Decision-Routen → typed React client → `Dubletten`-Ansicht. Subject-/Source-Summaries sind reine Read-Model-Daten. Es gibt keine Merge-Engine und keine Mutation der beteiligten Opportunity-/Posting-Identitäten oder ihrer Assessments, Decisions, Groups, ApplicationCases, Documents oder Published References.

