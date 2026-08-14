# Vocation – Read Models

**Status:** Draft 0.1

## 1. Grundsatz

Read Models sind zweckgebundene Projektionen. Sie besitzen keine eigene fachliche Datenhoheit und dürfen keine widersprüchlichen Kopien erzeugen.

## 2. JobListItem

Felder:

- Opportunity ID
- Title
- Company
- Primary Work Location
- Location Precision
- Tracking Status
- Priority
- Preferred Assessment Summary
- Risk Count
- Availability
- Freshness
- Group Memberships
- Preferred Posting Link Availability

## 3. JobDetailView

Enthält:

- Opportunity Header
- Company und Organization Unit
- Work Locations
- Postings nach Source
- Source References und External Links
- Observations nach Kategorie und Zeit
- External und Personal Assessments getrennt
- Risks
- Decisions
- Groups
- Availability History
- Duplicate Cases
- Change Summary

## 3A. ApplicationCaseView (implemented, Vocation-internal/private)

Die View zeigt ApplicationCase-Lifecycle, append-only Lifecycle Events, aktive und terminale historische Cases sowie aktuelle ApplicationMaterial-Metadaten. Die aktuelle Material-Revision wird aus der unveränderlichen Revision-Historie rekonstruiert. Es gibt noch keinen Endpoint für die vollständige Material-Revision-Historie und keine Dokumentinhalte oder Storage-Metadaten in der View. ApplicationCase und ApplicationMaterial bleiben vollständig Vocation-intern/private und erscheinen in keinem Published Contract.

Eine ApplicationMaterial-Revision kann semantisch null oder ein privates ApplicationDocument referenzieren. Normale Opportunity Read Models zeigen weder Payload noch Document Storage Metadata. Die implementierte Opportunity-Detail-Ansicht zeigt den revisionsgebundenen Dokumentstatus und die privaten Metadaten; Preview, Export/Download und vollständige Revision-History sind nicht implementiert; der private Slice-17-Zugriff `OpenApplicationDocument` ist separat beschrieben.

Slice 17 ergänzt den expliziten privaten `Öffnen`-Zugriff für das exakt angezeigte Dokument der aktuellen Material-Revision. Es gibt keinen Fallback auf eine andere/latest Revision. Die UI öffnet nicht automatisch; bei fehlendem Dokument gibt es keine Aktion. Content bleibt Vocation-intern/private und wird vor Rückgabe integritätsvalidiert.

## 4. OpportunityComparisonView (implemented)

Interner, nicht persistierter Read Model für eine temporäre Auswahl von mindestens 2 und höchstens 4 eindeutigen, existierenden Opportunities. Die Spaltenreihenfolge folgt exakt der angeforderten Opportunity-ID-Reihenfolge. Eine fehlende Opportunity oder ungültige Anzahl wird als Fehler gemeldet.

Jede Spalte enthält mindestens:

- Opportunity ID, Title, Company ID und Company Name
- WorkLocations mit Label und Precision
- Tracking Status
- Availability sowie Availability `last_checked_at` und `age_days`
- kompakte Group/Wave-Memberships

Zeilen oder Dimensionen:

- Company
- Title
- Technologies
- Tasks
- Seniority
- Experience Requirements
- Work Model
- Locations
- Salary
- Assessments
- Availability
- Freshness
- Opportunity-scoped Assessments

Research-Zellen verwenden ausschließlich Opportunity- und Posting-scoped Observations der sechs festgelegten Dimensionen. Keine Observations bedeutet `missing`; mehrere distinct Werte werden deterministisch, vorzugsweise neuestes Evidence zuerst mit stabilem ID-Tie-Break, als mehrere Werte dargestellt. Unterschiedliche Werte sind nicht automatisch contradictory. Personal Assessments zeigen nur die aktuelle Revision criterion-keyed, External Assessments nur Opportunity-scoped und ebenfalls ohne automatische Auswahl. Company-scoped Daten werden nicht kopiert. Risk bleibt mangels konkreter Read-Quelle außerhalb dieses V1-Read-Models.

Comparison ist implementiert, besitzt keine Persistenz, keine URLs/Browseraktionen und keine eigene Datenhoheit. Der Read Repository und der interne `POST /api/comparison/opportunities`-Endpoint liefern das Modell; die Desktop-Ansicht ist für 2–4 Spalten horizontal scrollbar und verlinkt in bestehende Vocation Details. Published Opportunity Overview 1.0 bleibt unverändert.

## 5. CompanyOverviewView

- Company Summary
- Locations
- Opportunities
- Company Assessments
- alternative Names
- aktive und historische Postings

## 6. GroupView / ApplicationWaveView

- Group Metadata: stable Group ID, name, optional description, type
- ordered Opportunity Items with explicit positions
- Statusverteilung
- Freshness und Availability Summary

`ApplicationWaveView` ist dieselbe Group-Sicht für Type `application_wave`; es gibt kein separates Wave-Aggregat. Opportunity List/Detail zeigen Memberships und unterstützen Group/Wave-Filter. Diese Read Models und die Group/Wave-Filter sind implementiert; die API ist unter `/api/groups` verfügbar.

## 7. MapProjection (implemented)

```json
{
  "projection_version": "1.0",
  "features": [
    {
      "feature_id": "map-feature-id",
      "opportunity_id": "opportunity-id",
      "company_id": "company-id",
      "title": "Junior Softwareentwickler",
      "company_name": "Example GmbH",
      "coordinates": {"lat": 53.6, "lon": 10.1},
      "precision": "exact_address",
      "tracking_status": "interesting",
      "availability": "available",
      "preview": {
        "subtitle": "Hamburg",
        "assessment": "7/10",
        "risk_count": 1
      },
      "groups": ["group-id"]
    }
  ]
}
```

Die interne Projection enthält pro aufgelöster WorkLocation mindestens `feature_id`, `work_location_id`, `opportunity_id`, `company_id`, Titel, Company Name, Location Label, Coordinates, WorkLocation Precision, Tracking Status, Availability und kompakte Group/Wave-Memberships. Nicht aufgelöste WorkLocations (`unmapped`) erzeugen kein Feature. Die Projection wird aus einer expliziten Opportunity-ID-Menge erzeugt, damit Karte und Liste filterkonsistent bleiben. `/api/map`, Leaflet/React Leaflet, Marker-Popups und die gemeinsamen List/Map-Filter sind implementiert. Clustering ist Renderer-Logik; OpenStreetMap-Tile-Attribution wird angezeigt.

Regeln:

- nur explizit kartierbare Locations,
- approximierte Features klar kennzeichnen,
- mehrere Opportunities an einem Standort dürfen geclustert werden,
- Browserlinks bleiben Source References,
- Pin-Klick öffnet keine externe URL automatisch.
- Pin-Klick öffnet in Slice 11 nur Vocation Preview/Detail; Browser-Navigation gehört zu Slice 12.

Die MapProjection bleibt damit URL-frei. Slice 12 leitet ExternalLink-Kandidaten separat aus einer Opportunity ID ab; sie sind kein Projection-Feld.

## 8. ExternalLinkView (implemented)

ExternalLink-Kandidaten werden aus bestehenden Posting-, Source- und SourceReference-Daten gelesen und enthalten Source, URL, Display Label, Posting Availability, Observed At und den Preferred-Marker. `/api/external-links` liefert die Read-/Open-Funktionen; es gibt keine ExternalLink-Tabelle. Opportunity Detail zeigt die Kandidaten und lokale No-Link/Browser-Fehlerzustände. Map-Popups laden diese Kandidaten separat und dedupliziert pro Opportunity; die MapProjection bleibt URL-frei.

## 8. ImportReportView

- Import Metadata
- Bundle Version
- Prompt Context Ref, sofern vorhanden
- Scope
- Result
- Counts
- Entry Results
- Errors
- Warnings
- affected Domain IDs

## 9. PromptPreviewView

- mode/type
- Bundle Version
- Prompt Version bei Updates
- Prompt Context Ref bei Updates
- rendered Prompt

## 10. PublishedOpportunityOverview (implemented, client-neutral)

Vocation-owned, versioned read projection for Wiiii Got This and other explicit clients. Contract 1.0 is frozen by `schemas/published-opportunity-overview-v1.schema.json`; the projection and local adapter are implemented and remain outside the internal React OpenAPI.

Der finale Contract 1.0 ist jetzt eingefroren: `capability`, `contract_version`, `publication` und `opportunities`. Die geschlossenen Opportunity-Objekte enthalten ausschließlich opaque Opportunity-/Company-Referenzen, Titel, Company, Work Locations und Posting Count. Es gibt keine URLs, Navigation, Personal-/Import-/Provenance-Daten, Availability/Freshness oder Schreibinformationen. Der lokale Adapter ist unter `/published/v1/opportunity-overview` implementiert und bleibt außerhalb der internen React OpenAPI.

- `contract_version`
- publication metadata: `publication_ref`, `generated_at`
- frozen opportunity overview payload

## 11. Published Map Projection 1.0 (implemented)

Client-neutral, transport-independent Published Vocation Capability for map-capable consumers. The canonical contract is `schemas/published-map-projection-v1.schema.json`, exposed at `GET /published/v1/map-projection` outside the internal React OpenAPI. A dedicated read-only publication repository/service reads only existing explicit MapLocationResolutions and emits URL-free features with opaque feature/opportunity/company refs, title, company, WorkLocation label/precision, and latitude/longitude. Empty features are valid and multiple mapped WorkLocations may produce multiple features for one Opportunity. Publication never geocodes, mutates, or resolves anything. Features are ordered deterministically by company name, opportunity title, WorkLocation label case-insensitively, then `feature_ref`. No personal, research, posting, source, availability, freshness, group, URL, provider, or internal-ID fields are included. Published Opportunity Overview 1.0 remains unchanged.

## 12. Availability/Freshness Integration (implemented on `dev`)

Interne Read Models exponieren abgeleitete Availability und die Freshness der Availability-Evidenz aus append-only Availability Observations. Diese Felder gehören nicht zum Published Opportunity Overview 1.0 Contract.

## 13. Publication Metadata

For the frozen Published Opportunity Overview 1.0 contract, current publication metadata
contains only `publication_ref` and `generated_at`. It does not define publication age,
data freshness, import time, or a stale indicator.
## Opportunity-Triage-Read-Model (v0.2.0)

Opportunity-Liste und Detail enthalten den Tracking Status und unterstützen Statusfilter. Die Detailansicht trennt `external_assessments`, aktuelle `personal_assessments`, `personal_assessment_history` und chronologische `decision_history`. Die historische Darstellung ist append-only und stammt aus Vocation-eigenen Tabellen; Research-Bundle-Daten bleiben externe Beobachtungen. Mutation-Fehler dürfen bereits geladene Read Models nicht leeren.

Für Slice 9 zeigen interne Read Models Posting-/Opportunity-Availability sowie availability-evidence Freshness (`last_checked_at`, `age_days`). Freshness hat keine Schwellenkategorie und ändert Availability nicht automatisch.

Die Desktop-Read-Workflow-Integration ist implementiert: Listenfilter und Availability-Badges sowie Detailansicht und append-only Availability-Historie sind verfügbar. Diese post-v0.3-Funktion bleibt außerhalb des Published Opportunity Overview 1.0 Contracts.
