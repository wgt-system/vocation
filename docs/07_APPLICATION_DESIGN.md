# Vocation – Application Design

**Status:** Draft 0.1

## 1. Zweck

Dieses Dokument beschreibt Application Use Cases, Commands, Queries, Abläufe und Fehlerfälle. Die Application Layer koordiniert Domänenobjekte und Infrastruktur, enthält aber keine zentrale Fachlogik.

## 2. Rollen

Version 1 kennt einen lokalen Nutzer. Es gibt kein allgemeines Benutzer- oder Rollensystem.

## 3. Commands

### List/Create/Edit/Activate/Deactivate/ReorderAssessmentCriteria

Vocation verwaltet seinen eigenen Criteria Catalog. Inkompatible semantische Änderungen an bereits verwendeten Kriterien werden abgelehnt und verlangen eine neue Criterion ID.

### GenerateResearchPrompt (implementiert)

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
6. generische Schutzregeln gegen die Ausgabe oder Mutation persönlichen Zustands einbetten.
7. Prompt rendern.
8. Prompt Run samt Criteria Snapshot speichern.
9. Prompt in UI anzeigen und Copy-to-Clipboard anbieten.

Output:

- Prompt Text
- Prompt Run ID
- Prompt Context Ref bei Updates
- Scope Summary
- Prompt Version
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
7. die Bundle-Version explizit dispatchen: Research Bundle `1.0` oder Research Update Bundle `2.0`.
8. beim Update den gespeicherten Prompt Context laden und Scope/Correlation validieren.
9. Identität prüfen und einen deterministischen Plan mit Blockern erzeugen.
10. bei fehlerfreiem Plan genau eine atomare Apply-Transaktion ausführen.
11. Import Report erzeugen.

Research Bundle `1.0` bleibt initial-only und wird ausdrücklich getrennt von Research Update Bundle `2.0` behandelt. Beim Update werden bestehende Company-, Opportunity- und Posting-Zeilen sicher wiederverwendet, ohne kanonische Zustände umzuschreiben; externe Evidence ist append-only. Blocker werden vor Domain-Mutation erkannt, danach wird das akzeptierte Update atomar angewendet. Identische Bundles werden nicht erneut angewendet.

Für v0.3 bleibt Research Bundle `1.0` unverändert und initial-only. Kontrollierte Updates verwenden Research Update Bundle `2.0` mit `prompt_context_ref`, opaque Correlation References und den Scopes `full_update`, `company_update`, `opportunity_update` oder `gap_filling`. GenerateResearchPrompt ist für Initial Research und alle vier Update-Modi implementiert. Availability Check Prompt-Erzeugung und der dedizierte Availability-Import sind ebenfalls implementiert; Availability/Freshness ist in den internen Opportunity-Read-Models und der API abgeleitet sichtbar. Updates persistieren Prompt Run, Prompt Context Ref, expliziten Scope, Prompt Version und Bundle Version `2.0`.

Output:

- Import ID
- Result
- created/reused/unchanged counts
- Warnings und Errors

### ChangeTrackingStatus

Nur persönliche Aktion. External Imports dürfen diesen Command nicht auslösen.

### AddPersonalAssessment

Erzeugt ein Personal Assessment und überschreibt kein External Assessment.

Research Update Bundle `2.0` darf Personal Assessments, Tracking Status, Opportunity Decisions, Exclusion/Restore und Groups/Waves weder enthalten noch mutieren.

### ExcludeOpportunity

Erfordert mindestens einen Exclusion Reason.

### RestoreOpportunity

Hebt eine frühere Einschränkung nachvollziehbar auf.

### CreateOpportunityGroup (implemented)

Erzeugt eine OpportunityGroup mit stabiler Group ID, nichtleerem Namen, optionaler Beschreibung und Type `general` oder `application_wave`; es entstehen keine Opportunity-Zustandsänderungen.

### EditOpportunityGroup / DeleteOpportunityGroup (implemented)

Edit ändert nur die Gruppenmetadaten. Delete entfernt die Memberships der Group, aber niemals Opportunities oder deren Zustand.

### AddOpportunityToGroup / RemoveOpportunityFromGroup (implemented)

Add fügt eine Membership am Ende ein; Remove entfernt nur die Membership. `(group_id, opportunity_id)` ist eindeutig.

### ReorderOpportunityGroup (implemented)

Erhält den vollständigen geordneten Member-Satz und normalisiert die Positionen deterministisch.

### ResolveDuplicateCase

Im v0.3 erzeugt oder verwendet der Update-Plan ausschließlich ungelöste Duplicate Cases aus möglicher Duplicate-Evidence. Es gibt noch keine bestätigte Auflösung und keinen Merge. Spätere Entscheidungen können folgende Ergebnisse liefern:

- confirmed duplicate,
- confirmed distinct,
- related but distinct,
- keep unresolved.

### OpenPostingInBrowser (implementiert)

Input:

- Posting ID oder Opportunity ID plus optionale Source Selection

Ablauf:

1. gültige ExternalLink-Kandidaten ableiten.
2. explizite Posting-Auswahl verwenden oder PreferredPostingSelector anwenden.
3. ExternalLinkPolicy anwenden.
4. nur die validierte URL an den Browser Adapter übergeben.
5. Erfolg oder Fehler anzeigen.

Fehler:

- kein Posting verfügbar,
- Link ungültig,
- Scheme nicht erlaubt,
- Browserstart fehlgeschlagen.

Es gibt in V1 keine Navigation beim Laden von Details, der Karte, eines Markers oder beim Ändern von Filtern und keine Navigation-Audit-/Event-Persistenz.

Die Read-/Open-Endpunkte sind unter `/api/external-links` verfügbar; typed internes OpenAPI und Frontend-Client sind implementiert. Opportunity Detail zeigt Source, Availability, Observed At und den Preferred-Marker, unterstützt Default-/Preferred- sowie explizites Posting-Öffnen und zeigt No-Link- und lokale Browser-Fehlerzustände.

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

Group-Memberships werden in Liste und Detail angezeigt und können als Filter verwendet werden. Die implementierte API ist unter `/api/groups` verfügbar; die React Groups & Waves UI unterstützt Group CRUD sowie Add, Remove und Reorder Membership.

### Group Queries (implemented)

- Group list
- Group detail with ordered Opportunities
- Opportunity list/detail memberships
- Opportunity filtering by Group/Wave

### CompareOpportunities

Vergleicht ausgewählte Opportunities und zeigt fehlende oder widersprüchliche Daten explizit.

### GetMapProjection (implemented)

Liefert generische Map Features für eine explizite Menge von Opportunity IDs, typischerweise die aktuell gefilterte Opportunity-Menge. Es gibt ein Feature pro aufgelöster WorkLocation.

Jedes Feature enthält:

- Feature ID
- Opportunity ID
- Company
- Title
- Coordinates
- Precision
- Status
- Preview
- Posting-Link-Verfügbarkeit (ohne URLs)

Map Features enthalten zusätzlich WorkLocation Label, WorkLocation Precision, Availability und kompakte Group/Wave-Memberships. Ein Pin öffnet nur Vocation Preview/Detail; externe URLs werden in Slice 11 nicht geöffnet.

Die Map API ist unter `/api/map` implementiert. Explizite Geocodierung/Manuell-Auflösung und das Löschen einer Resolution sind Nutzeraktionen; der provider-neutrale Geocoder-Port ist mit einem konfigurierbaren Nominatim-Adapter hinterlegt. Leaflet/React Leaflet rendert die Karte mit OpenStreetMap-Tile-Attribution; Renderer und Provider bleiben austauschbare Infrastruktur.

### GetPromptPreview

Zeigt Template, Scope und eingebetteten Kontext vor dem Kopieren.

### GetImportReport

Zeigt pro Entry Ergebnis, Warnungen, Fehler und betroffene Objekte.

### Publish/Get Opportunity Overview

Read-only capability boundary owned by Vocation Data Publication. The Publication Adapter builds a versioned, client-neutral `Opportunity Overview` projection and its Publication Metadata. The 1.0 JSON field schema is now frozen by `schemas/published-opportunity-overview-v1.schema.json`. Publication never becomes a second domain authority.

Der JSON-Vertrag ist in `schemas/published-opportunity-overview-v1.schema.json` eingefroren. Der lokale Adapterpfad `/published/v1/opportunity-overview` ist implementiert, unabhängig von `/api/opportunities`, schreibfrei und darf das Artefakt nicht umdeuten. Ein späteres Relay transportiert dasselbe Artefakt unverändert.

## 5. Desktop UI-Flows

### Prompt Flow (implementiert)

1. Recherchemodus und Scope wählen.
2. Prompt generieren.
3. Vorschau prüfen.
4. Prompt kopieren, speichern oder extern verwenden.
5. zurückgegebenes JSON inline importieren.
6. Import Report prüfen.

### Map Flow (implementiert)

1. Filter setzen.
2. Karte öffnen.
3. Pin anklicken.
4. Opportunity-Vorschau öffnen.
5. Detailansicht öffnen.

Eine manuelle oder provider-neutrale Geocoder-Auflösung einer WorkLocation wird nur durch explizite Nutzeraktion ausgelöst. Die Karte und Liste verwenden dasselbe Opportunity-Filterergebnis; Clustering bleibt Renderer-Präsentationslogik und ist kein Domain-Zustand.

Die UI bietet explizite Geocode-, Manual- und Delete-Resolution-Aktionen sowie Marker-Popups mit Navigation zu Vocation Details.

Die implementierten Marker-Popups laden ExternalLink-Kandidaten separat per Opportunity ID, deduplizieren das Laden pro Opportunity und bieten `Originalanzeige öffnen` oder Source-Auswahl an. URLs sind kein Bestandteil der MapProjection.

### Import Flow

1. Datei oder Clipboard wählen.
2. Vorprüfung.
3. Import ausführen.
4. Bericht prüfen.
5. problematische Einträge filtern.

## 6. Cross-device Published Read Use Cases

- Wiiii Got This kann geeignete Published Vocation Capabilities auf Windows und iPhone darstellen.
- Die letzte Published Projection bleibt nutzbar, wenn der Windows-PC ausgeschaltet ist.
- Publication Snapshot Age wird getrennt von Domain Freshness angezeigt.

Nicht erforderlich:

- Prompt-Erzeugung
- Import
- Duplicate Resolution
- komplexe Pflege

Vocation bleibt Eigentümer von Data Publication; ein Relay/Storage ist optional und domänenblind.

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
