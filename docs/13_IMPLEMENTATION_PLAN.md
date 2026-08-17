# Vocation – Implementation Plan

**Status:** v0.3.0 released baseline; post-v0.3 development continues on `dev`.

## Phase 0 – Spezifikationsprüfung

Vor Produktcode werden maßgebliche Dokumente auf Widersprüche, Blocker, untestbare Kriterien und fehlende Vertragsdetails geprüft.

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

## Slice 11 – Karte (implementiert auf `dev`, generische Infrastruktur zu Orientation migriert)

- Work Locations
- MapProjection
- Renderer
- Filterkonsistenz
- Pin Preview

V1 führte `MapLocationResolution` als Vocation-owned Supporting Data pro WorkLocation ein. Persistence, explizite Manual-/Geocoder-Auflösung, interner MapProjection-Read-Path, `/api/map`, gemeinsame List/Map-Filter über die aktuell sichtbaren Opportunity IDs sowie Geocode/Manual/Delete-UI bleiben implementiert und Vocation-owned. Resolution ist nicht append-only Evidence oder Decision History, überschreibt keine WorkLocation Precision und wird nur explizit durch den Nutzer ausgelöst. Keine automatische/background Geocodierung, kein Address Crawling und keine Status-/Personal-/Research-/Availability-Mutation.

Die ursprünglich in Vocation implementierten generischen Nominatim- und Leaflet/React-Leaflet-Adapter wurden nach der systemweiten Orientation-Ownership-Entscheidung ersetzt. Der Vocation `Geocoder`-Port nutzt jetzt `OrientationGeocoder` gegen Orientation Place Search (`GET /api/v1/places/search`). Die React-Karte nutzt `OrientationMapFrame` und den gepinnten Orientation Embed Host über `orientation.host-bridge` 1.0. Vocation adaptiert weiterhin die fachlich autoritative MapProjection, Information und Action References; Orientation rendert die generische Spatial Scene und gibt Action-Aktivierungen an Vocation zurück. Published Opportunity Overview 1.0 bleibt unverändert.

## Slice 12 – External Links (implementiert auf `dev`)

- PreferredPostingSelector
- ExternalLinkPolicy
- Browser Adapter
- Quellenwahl im Pin und Detail

V1 definiert ExternalLink als abgeleiteten Read-/Application-Wert ohne eigene Persistenz. Implementiert sind ExternalLinkPolicy, deterministischer PreferredPostingSelector, SQLAlchemy Read-Adapter, SystemBrowserAdapter, `/api/external-links`, typed interne OpenAPI-/Frontend-Clients, Opportunity-Detail-Workflow sowie Map-Navigation mit dedupliziertem Link-Laden pro Opportunity. Die Policy akzeptiert nur absolute HTTPS-URLs mit Host und prüft lokal ohne URL-Probing. Availability, Source Type, `observed_at` und Posting ID bestimmen das Ranking; explizite Auswahl wird nicht gespeichert. `OpenPostingInBrowser` ist ausschließlich Nutzeraktion. Die Orientation Map Surface erhält nur Vocation-definierte Action References; Auswahl und Browseröffnung bleiben Vocation-owned. Research Contracts und Published Opportunity Overview 1.0 bleiben unverändert.

## Slice 13 – Vergleich (implementiert auf `dev`)

- Comparison Read Model
- UI

V1 definiert `OpportunityComparisonView` als internen, read-only und nicht persistierten Vergleich für 2 bis 4 explizit geordnete, existierende Opportunities. Implementiert sind `POST /api/comparison/opportunities`, SQLAlchemy Comparison Read Repository, typed OpenAPI-/Frontend-Client, temporäre Desktop-Auswahl, horizontal scrollbar 2–4-Spalten-UI und Vocation-Detail-Navigation. Die Ansicht zeigt Summary, Availability-evidence Freshness, Groups/Waves, sechs Research-Dimensionen und Opportunity-scoped Assessments mit explizitem Missing-State und deterministischer Evidenzreihenfolge. Sie ist kein Ranking, Scoring, Recommendation, Winner Selector oder neue Assessment-Domäne. Es gibt keine inferred Contradictions, keine URLs/Browser-Aktionen und keine Mutation. Eine konkrete Risk-Read-Quelle ist nicht implementiert; Risk-Vergleich bleibt spätere Arbeit. Published Opportunity Overview 1.0 bleibt unverändert.

## Slice 14 – Client-neutral Published Capability expansion

### Published Map Projection 1.0 (implementiert auf `dev`)

Der client-neutrale, transport-unabhängige Contract `schemas/published-map-projection-v1.schema.json` ist eingefroren und unter `GET /published/v1/map-projection` implementiert. Ein dedizierter read-only Publication Repository/Service publiziert ausschließlich bestehende explizite MapLocationResolutions als URL-freie Features mit opaque Refs, Titel, Company, WorkLocation Precision und Koordinaten. Publication geocodiert, mutiert oder resolved nichts. Features werden deterministisch nach Company Name, Opportunity Title, WorkLocation Label case-insensitiv und `feature_ref` geordnet. Empty Features sind gültig; mehrere mapped WorkLocations können mehrere Features je Opportunity erzeugen. Der Endpoint bleibt außerhalb der internen React OpenAPI; persönliche Zustände, Availability/Freshness, Groups/Waves, URLs, Provider-, Research-, Import-, Posting- und Source-Daten werden nicht exponiert. Published Opportunity Overview 1.0 bleibt unverändert.

Die lokale Vocation→Orientation-Map-Komposition ändert diesen geschlossenen Contract nicht. Der Architecture Control Plane erlaubt reichere provider-owned Spatial Projections, verlangt für Cross-Context-Publication aber einen versionierten Nachfolger statt einer stillen Änderung von Published Map Projection 1.0.

## Slice 15 – Application Case and private Application Material (implementiert auf `dev`)

Vocation besitzt ApplicationCase-Fachsemantik als Aggregate pro Opportunity, getrennt vom Opportunity Tracking Status. Implementiert sind die eingefrorenen Lifecycle-Semantiken, das immutable Domain Model, Alembic `0011`, der DB-Invariant für einen aktiven Case, append-only Lifecycle-/Material-Revision-Historie, SQLAlchemy Repository, ApplicationCaseService, interne FastAPI-Endpunkte, typed OpenAPI-/Frontend-Client, Opportunity-Detail-React-UI sowie fokussierte Domain-/Migration-/Service-/API-/Frontend-Tests. Research/Availability, automatische Submission, E-Mail/Calendar-Übergänge, tatsächliche CV-/Cover-Letter-Inhalte, File Upload, PDF/LaTeX/Document Rendering, Storage-/Encryption-Implementierung, private Cross-device-Transporte, WGT und Conveyance bleiben aus diesem Slice ausgeschlossen. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben unverändert.

## Slice 16 – Private Application Document Content (implementiert auf `dev`)

Vocation besitzt die semantische `ApplicationDocument`-Zuordnung an genau einer immutable ApplicationMaterial-Revision. Implementiert sind Domain-Metadata aus supplied bytes, Alembic `0012`, `application_documents`, Composite FK und Unique-Invariant pro Material-Revision, `ApplicationDocumentStore`-Port, `FilesystemApplicationDocumentStore`, SQLAlchemy Repository, ApplicationDocumentService mit write/read-back integrity verification, private interne FastAPI-Endpunkte, typed Frontend Client und der bestehende ApplicationCasePanel-Upload-Workflow. Lokale Konfiguration verwendet `data/application-documents` in Development, `%LOCALAPPDATA%\\Vocation\\application-documents` packaged/frozen oder `VOCATION_DOCUMENT_STORE_DIR` als Override. Payload bytes werden außerhalb relationaler Tabellen gespeichert; physische Dateinamen leiten sich aus `sha256(storage_ref.encode("utf-8"))` ab und sind keine Domainsemantik.

Erlaubt sind `application/pdf`, `text/plain` und `text/markdown`; Original-Dateiname, Media Type, Byte Size, SHA-256 und Created At werden als private Metadata behandelt. Neue Inhalte erfordern neue Material-Revisionen; es gibt kein In-place-Replacement, Delete oder Content-Deduplication. Preview, Export/Download, Editing, Templates, PDF/LaTeX, Encryption at Rest, Cross-device Encryption, Synchronization/Replication, WGT/Conveyance-Integration und Submission/Email/Calendar-Automation bleiben Nicht-Ziele. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben unverändert. Künftige Cross-Context-Arbeit folgt `wgt-system/architecture`.

## Slice 17 – Private Application Document Access (implementiert auf `dev`)

Slice 17 ist auf `dev` implementiert. Der read-only Use Case `OpenApplicationDocument` nutzt die bestehende Integritätsprüfung des `ApplicationDocumentStore` für ein exakt bestimmtes, immutable ApplicationDocument an einer ApplicationMaterial-Revision. Der bestehende ApplicationDocumentStore liest den Payload und validiert Byte Size sowie SHA-256 vor jeder nutzbaren Rückgabe. Die bestehende interne/private Content-Grenze `GET /api/application-documents/{document_id}/content` liefert die exakten Payload Bytes und den persistierten Media Type, ohne Storage Reference, Pfad, hashed physical filename oder Store Root; sie ist kein Published Contract.

Die React ApplicationCasePanel-Oberfläche bietet für ein vorhandenes Dokument der aktuell angezeigten Revision die explizite Aktion `Öffnen` und verwendet exakt das geladene `document.id` in einem neuen Browsing-Kontext (`target="_blank"`, `rel="noopener noreferrer"`). Browser-supported PDF-/Text-Handhabung ist zulässig; eingebettetes Preview/Rendering, Export/Save-as, Edit/Delete/Replace, Cross-device Integration, WGT/Conveyance-Zugriff und neue Lifecycle-/Tracking-Zustände gehören nicht zu Slice 17. Die Implementierung folgt der autoritativen `wgt-system/architecture` für künftigen privaten Cross-device-Zugriff.


## Slice 18 – Duplicate Case Resolution (implementiert auf `dev`)

Vocation kann bestehende Opportunity- und Posting-DuplicateCases jetzt explizit und historisiert reviewen. Implementiert sind `DuplicateDecision` mit den vier eingefrorenen Outcomes und nichtleerem Grund, Alembic `0013`, append-only SQLAlchemy-Persistenz, aktuelle Review-Sicht aus der letzten Decision, interne `/api/duplicate-cases`-Read-/Decision-Routen, generierte TypeScript-API-Typen sowie die React-Ansicht `Dubletten` mit offenen/entschiedenen/allen Fällen und vollständiger Decision History.

`confirmed_duplicate` bleibt reine Klassifikation. Slice 18 führt keinen Merge, keine Löschung, kein Canonical-Survivor-Modell, kein Re-Parenting und keine Übertragung von Assessments, Decisions, Groups/Waves, ApplicationCases, ApplicationMaterials oder ApplicationDocuments aus. Research-/Availability-Imports verändern Duplicate Decisions nicht. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben unverändert. Eine spätere Merge-Capability benötigt eine eigene explizit eingefrorene Semantik.

## Cross-cutting Migration – Orientation Integration (implementiert auf `dev`)

Nach Annahme von Orientation als generischem Geospatial-Bounded-Context wurden die entsprechenden Vocation-Duplikate entfernt bzw. ersetzt:

- direkter Nominatim-Adapter entfernt;
- `OrientationGeocoder` konsumiert Orientation Place Search über eine konfigurierte Base URL (`VOCATION_ORIENTATION_BASE_URL`, Default `http://127.0.0.1:8080`);
- React Leaflet/Leaflet und die zugehörigen Vocation-Renderer-Abhängigkeiten entfernt;
- Orientation Embed Host als gepinntes statisches Artefakt unter `frontend/public/orientation-map/` eingebunden;
- `ORIENTATION_SOURCE_SHA.txt` dokumentiert die verwendete Orientation-Source-Revision;
- `OrientationMapFrame` adaptiert Vocation-owned Features/Information/Actions in `orientation.host-bridge` 1.0;
- Vocation verarbeitet Details-/External-Link-Aktionen weiterhin selbst.

Diese Migration verändert keine Vocation-owned Work-Location-/Precision-/Opportunity-/External-Link-Semantik und keinen eingefrorenen Published Contract. Routing aus Orientation v0.3.0 wird dadurch nicht automatisch zu einer Vocation-Anforderung.

## Weitere mögliche Produktarbeit

- weitere client-neutrale Published Vocation Capabilities, nur bei konkretem Consumer-Szenario;
- WGT/iOS/Conveyance-Integration geeigneter Published/privater Capabilities;
- private Document-Folgeslices wie Preview/Export/Editing/Generation nur nach eigener Semantik-Freigabe;
- reichhaltiger Nachfolger von Published Map Projection 1.0 nur bei konkretem Cross-Context-Bedarf;
- keine iOS-App in Vocation.

## Ausführungsworkflow

Remote GitHub-Arbeit wird standardmäßig direkt über den GitHub-Connector ausgeführt: Repository-Inspektion, Dateien/Branches/PRs/Issues und Remote-Verifikation werden nicht an lokale Worker delegiert, wenn der Connector die Aufgabe vollständig abdeckt.

Lokale Worker/Subagents werden nur für Aufgaben eingesetzt, die echten lokalen Dateisystem-, Build-, Runtime-, Geräte- oder Umgebungszugriff benötigen. Lokale Installationen oder Toolchain-Änderungen benötigen vor Ausführung die ausdrückliche Zustimmung des Nutzers.

## Done-Kriterien je Slice

- maßgebliche Dokumente genannt,
- relevante verfügbare Tests/Checks grün oder nicht verfügbare lokale Checks transparent benannt,
- keine stillen Vertragsänderungen,
- ADRs aktualisiert, wenn eine echte Architekturentscheidung getroffen wurde,
- Acceptance Tests nachvollziehbar erfüllt,
- Vocation-Domainownership und lokale Autorität bleiben erhalten,
- akzeptierte generische System-Capabilities werden nicht ohne Architekturentscheidung dupliziert.

## v0.2.0 – Persönliche Triage

Der v0.2.0-Scope umfasst versionierte Personal Assessments, Tracking Status, Decision History, Exclusion/Restore sowie Desktop-API- und React-Steuerung. Nicht enthalten bleiben Update-Bundles, fuzzy matching, Rankings, Gruppen/Waves, Maps, Published Vocation Capabilities, Crawling, kostenpflichtige LLM-APIs und Authentifizierung.

## v0.3.0 – Implementierungsstand

Issue #7 – Research Update Bundle 2.0 Contract: abgeschlossen.

Issue #8 – deterministische Identität und ungelöste Duplicate Cases: abgeschlossen.

Issue #9 – Prompt Context Persistence, read-only Planning und atomarer Update Import: abgeschlossen.

Issue #10 – scoped prompting und Desktop-Update-Workflow: abgeschlossen. Research Bundle `1.0` bleibt unverändert und initial-only. Vocation v0.3.0 enthält Research Update Bundle 2.0, scoped Full/Company/Opportunity/Gap Filling updates, Prompt Context Snapshots und opaque Correlation References, deterministische Posting-Identität, ungelöste Duplicate Cases ohne automatischen Merge, read-only Planning und atomaren Update Apply, PromptRun/ResearchImport-Traceability, den vollständigen Desktop Research Prompt preview/copy/save/import workflow sowie die implementierte Published Opportunity Overview 1.0 Publication auf `dev`. Issue #13 ist end-to-end implementiert: Availability Prompt generation, dedizierter Availability Import, Availability/Freshness Read Models/API sowie React/Desktop-Workflow mit Listenfiltern, Badges und Detail-/Historienansicht. Issue #14 Groups/Waves, Issue #15 Map, Issue #16 External Links und Issue #21 Opportunity Comparison sind end-to-end auf `dev` implementiert; Research contracts und Published Opportunity Overview 1.0 bleiben unverändert. Slice 15 ist implementiert: ApplicationCase und private ApplicationMaterial sind Vocation-eigene Domänensemantik mit der in diesem Abschnitt dokumentierten Persistenz-, Service-, API- und UI-Umsetzung.
