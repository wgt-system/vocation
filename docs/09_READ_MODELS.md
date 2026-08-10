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

## 4. OpportunityComparisonView

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
- Risks
- Availability
- Freshness
- Personal Status

Fehlende und widersprüchliche Werte werden explizit dargestellt.

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

## 11. Published Map Projection (future, client-neutral)

Future client-neutral projection for map-capable consumers. It is not a mobile-specific contract and does not change Vocation ownership of Work Locations.

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
