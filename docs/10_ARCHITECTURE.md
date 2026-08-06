# Vocation – Architecture

**Status:** Draft 0.1

## 1. Architekturziele

- eigenständig startbare Desktop-Anwendung,
- klare Domain/Application/Infrastructure-Grenzen,
- keine Abhängigkeit von Wiiii Got This,
- versionierte Import- und Read Contracts,
- read-heavy Nutzung,
- lokale Datenhoheit,
- spätere mobile Read Integration,
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

## 3. Empfohlene Technologieentscheidung

Die endgültige Entscheidung bleibt ADR-pflichtig. Eine plausible Version-1-Kombination:

- Backend/Application: Python
- lokale API: FastAPI oder Flask
- Frontend: React/Vite
- Datenbank: SQLite
- Karte: Leaflet/OpenStreetMap
- Schema: JSON Schema
- Tests: pytest plus Frontend-Testframework

Diese Auswahl ist keine Domänenentscheidung.

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
- später HTTP Read API
- später mobile Contracts

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

## 6. Prompt-Dateien

Prompt Templates liegen versioniert unter `prompts/`.

Die Runtime darf Templates laden und mit einem Prompt Context Snapshot rendern.

Prompt Templates enthalten keine geheimen oder benutzerspezifischen Daten außerhalb des expliziten Scopes.

## 7. Import Pipeline

```text
File/Clipboard
→ Parse
→ Schema Validate
→ Contract Validate
→ Fingerprint
→ ACL Translation
→ Identity Resolution
→ Domain Commands
→ Transaction
→ Import Report
```

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

## 10. Mobile Integration

Vocation veröffentlicht später read-only Verträge oder Snapshots.

Mögliche Varianten:

- lokaler LAN-Service,
- manueller Snapshot,
- später Synchronisationsdienst.

Version 1 legt keine Cloud fest.

## 11. Packaging

Desktop-Version soll mit einem einfachen Startvorgang ausgeliefert werden. Separate manuelle Starts von Frontend und Backend sind für den Nutzer nicht das Ziel.

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

## 14. Architekturgrenzen

Nicht erlaubt:

- Shared Database,
- direkte Cross-Context Imports von Domain Classes,
- UI schreibt direkt in Datenbank,
- Importparser enthält Merge-Entscheidungslogik,
- Map-Renderer entscheidet Work Location,
- Browseradapter wählt Preferred Posting.
