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

- Group Metadata
- Opportunity Items
- Reihenfolge
- Statusverteilung
- Freshness und Availability Summary

## 7. MapProjection

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
      "posting_links": [
        {
          "posting_id": "posting-id",
          "source_name": "Company Careers",
          "url": "https://example.com/job",
          "preferred": true
        }
      ]
    }
  ]
}
```

Regeln:

- nur explizit kartierbare Locations,
- approximierte Features klar kennzeichnen,
- mehrere Opportunities an einem Standort dürfen geclustert werden,
- Browserlinks bleiben Source References,
- Pin-Klick öffnet keine externe URL automatisch.

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

## 10. PublishedOpportunityOverview (planned, client-neutral)

Vocation-owned, versioned read projection for Wiiii Got This and other explicit clients. The first contract slice defines the boundary and tests without freezing the final JSON field schema.

Der finale Contract 1.0 ist jetzt eingefroren: `capability`, `contract_version`, `publication` und `opportunities`. Die geschlossenen Opportunity-Objekte enthalten ausschließlich opaque Opportunity-/Company-Referenzen, Titel, Company, Work Locations und Posting Count. Es gibt keine URLs, Navigation, Personal-/Import-/Provenance-Daten, Availability/Freshness oder Schreibinformationen. Der lokale Adapter ist für `/published/v1/opportunity-overview` geplant.

- Publication Snapshot Metadata
- projection version
- client-neutral opportunity overview data
- explicit publication age

## 11. Published Map Projection (future, client-neutral)

Future client-neutral projection for map-capable consumers. It is not a mobile-specific contract and does not change Vocation ownership of Work Locations.

## 12. DataSnapshotMetadata

- Snapshot ID
- generated at
- Vocation data version
- latest import time
- stale indicator
- supported contracts
## Opportunity-Triage-Read-Model (v0.2.0)

Opportunity-Liste und Detail enthalten den Tracking Status und unterstützen Statusfilter. Die Detailansicht trennt `external_assessments`, aktuelle `personal_assessments`, `personal_assessment_history` und chronologische `decision_history`. Die historische Darstellung ist append-only und stammt aus Vocation-eigenen Tabellen; Research-Bundle-Daten bleiben externe Beobachtungen. Mutation-Fehler dürfen bereits geladene Read Models nicht leeren.
