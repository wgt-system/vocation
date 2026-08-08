# Vocation – Application Design

**Status:** Draft 0.1

## 1. Zweck

Dieses Dokument beschreibt Application Use Cases, Commands, Queries, Abläufe und Fehlerfälle. Die Application Layer koordiniert Domänenobjekte und Infrastruktur, enthält aber keine zentrale Fachlogik.

## 2. Rollen

Version 1 kennt einen lokalen Nutzer. Es gibt kein allgemeines Benutzer- oder Rollensystem.

## 3. Commands

### List/Create/Edit/Activate/Deactivate/ReorderAssessmentCriteria

Vocation verwaltet seinen eigenen Criteria Catalog. Inkompatible semantische Änderungen an bereits verwendeten Kriterien werden abgelehnt und verlangen eine neue Criterion ID.

### GenerateResearchPrompt

Input:

- Prompt Type
- Prompt Scope
- optionale Auswahl von Companies, Opportunities oder Feldern
- gewünschte Bundle Version
- Search Profile und Constraints für Initial Research

Ablauf:

1. Scope validieren.
2. Prompt Template laden.
3. minimalen Context Snapshot erzeugen.
4. alle aktiven Assessment Criteria mit Version/Snapshot einbetten.
5. den vollständigen Bundle-Output-Contract einbetten.
6. geschützte Personal Decisions kennzeichnen.
7. Prompt rendern.
8. Prompt Run samt Criteria Snapshot speichern.
9. Prompt in UI anzeigen und Copy-to-Clipboard anbieten.

Output:

- Prompt Text
- Prompt Run ID
- Scope Summary
- erwartete Bundle Version

Fehler:

- leerer Scope,
- ungültige referenzierte IDs,
- Template-Version fehlt,
- Kontext überschreitet konfigurierte Größe.

### ImportResearchBundle

Input:

- Datei oder Clipboard-Text

Ablauf:

1. Input lesen.
2. JSON parsen.
3. Bundle Version erkennen.
4. Schema validieren.
5. Fingerprint berechnen.
6. frühere Importe prüfen.
7. über ImportTranslator übersetzen.
8. Identität und Dubletten prüfen.
9. Domänenänderungen anwenden.
10. Import Report erzeugen.

Im ersten Meilenstein ist der Import pro Bundle vollständig atomar und akzeptiert ausschließlich Initial Research Bundles. Blockierende Fehler führen zu keinen fachlichen Änderungen. Identische kanonische Bundles werden nicht erneut angewendet.

Output:

- Import ID
- Result
- created/updated/unchanged counts
- Warnings und Errors

### ChangeTrackingStatus

Nur persönliche Aktion. External Imports dürfen diesen Command nicht auslösen.

### AddPersonalAssessment

Erzeugt ein Personal Assessment und überschreibt kein External Assessment.

### ExcludeOpportunity

Erfordert mindestens einen Exclusion Reason.

### RestoreOpportunity

Hebt eine frühere Einschränkung nachvollziehbar auf.

### CreateOpportunityGroup

Erzeugt allgemeine Group oder Application Wave.

### AddOpportunityToGroup / RemoveOpportunityFromGroup

Verändert keine Opportunity-Identität.

### ResolveDuplicateCase

Mögliche Ergebnisse:

- confirmed duplicate,
- confirmed distinct,
- related but distinct,
- keep unresolved.

### OpenPostingInBrowser

Input:

- Posting ID oder Opportunity ID plus optionale Source Selection

Ablauf:

1. Preferred Posting bestimmen oder Auswahl anzeigen.
2. ExternalLinkPolicy anwenden.
3. explizite Nutzeraktion bestätigen.
4. OS Browser Adapter aufrufen.
5. Ergebnis oder Fehler anzeigen.
6. optional Audit Event speichern.

Fehler:

- kein Posting verfügbar,
- Link ungültig,
- Scheme nicht erlaubt,
- Browserstart fehlgeschlagen.

## 4. Queries

### GetJobList

Filter:

- Tracking Status
- Group/Wave
- Company
- Technology
- Location
- Availability
- Freshness
- Assessment
- Risk
- Textsuche

### GetJobDetail

Liefert:

- Opportunity Summary
- Postings und Links
- Observations
- Assessments
- Decisions
- Risks
- Locations
- Groups
- Duplicate Cases
- History Summary

### CompareOpportunities

Vergleicht ausgewählte Opportunities und zeigt fehlende oder widersprüchliche Daten explizit.

### GetMapProjection

Liefert generische Map Features für den aktuell gesetzten Filter.

Jedes Feature enthält:

- Feature ID
- Opportunity ID
- Company
- Title
- Coordinates
- Precision
- Status
- Preview
- verfügbare Posting Links

### GetPromptPreview

Zeigt Template, Scope und eingebetteten Kontext vor dem Kopieren.

### GetImportReport

Zeigt pro Entry Ergebnis, Warnungen, Fehler und betroffene Objekte.

## 5. Desktop UI-Flows

### Prompt Flow

1. Recherchemodus wählen.
2. Scope wählen.
3. Vorschau prüfen.
4. Prompt kopieren.
5. extern recherchieren.
6. JSON importieren.

### Map Flow

1. Filter setzen.
2. Karte öffnen.
3. Pin anklicken.
4. Opportunity-Vorschau öffnen.
5. Detailansicht oder Posting-Quelle auswählen.
6. Originalanzeige im Browser öffnen.

### Import Flow

1. Datei oder Clipboard wählen.
2. Vorprüfung.
3. Import ausführen.
4. Bericht prüfen.
5. problematische Einträge filtern.

## 6. Mobile Read-only Use Cases

- Job List lesen
- Details lesen
- Map Projection lesen
- Gruppen lesen
- Freshness/Data Snapshot anzeigen
- Originalanzeige nach Tap im Browser öffnen

Nicht erforderlich:

- Prompt-Erzeugung
- Import
- Duplicate Resolution
- komplexe Pflege

## 7. Transaktionsgrenzen

- einzelner persönliche Command atomar,
- Bundle-Import je nach Vertrag vollständig atomar oder dokumentiert partiell,
- Version 1 bevorzugt atomaren Import pro Bundle,
- Read Models dürfen nachgelagert aktualisiert werden, zunächst synchron.

## 8. Fehlerformat

Application Errors enthalten:

- Code
- User Message
- technische Details optional
- betroffener Pfad oder Objekt-ID
- Recoverability
- vorgeschlagene Aktion

## 9. Nicht-Ziele

- kein automatisches Browser-Crawling,
- keine LLM-API,
- kein Bewerbungsversand,
- keine automatische externe Navigation,
- keine Plattformlogik von Wiiii Got This.
## Persönliche Triage-Commands (v0.2.0)

Die Anwendung bietet `CreatePersonalAssessment`, `RevisePersonalAssessment`, `ChangeTrackingStatus`, `ExcludeOpportunity` und `RestoreOpportunity`. Create und Revise sind getrennt; Create liefert einen Konflikt, wenn bereits ein aktuelles Assessment für Opportunity/Criterion existiert. Revise akzeptiert ausschließlich die aktuelle Revision. Restore verwendet ohne Zielstatus `active_exclusion.previous_status`; ein expliziter nicht ausgeschlossener Zielstatus ist optional. Die zugehörigen Queries liefern aktuelle und historische Personal Assessments sowie chronologische Decision History. Die Commands sind atomar; eine ungültige Eingabe erzeugt keinen Teilzustand. Die Services kennen nur `PersonalTriageRepository`- und `CriteriaRepository`-Ports.
