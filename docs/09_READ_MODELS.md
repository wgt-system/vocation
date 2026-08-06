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
- Scope
- Result
- Counts
- Entry Results
- Errors
- Warnings
- affected Domain IDs
- Link zum zugehörigen Prompt Run, sofern vorhanden

## 9. PromptPreviewView

- Prompt Type
- Prompt Version
- Scope Summary
- included Context Items
- protected fields note
- expected Bundle Version
- rendered Prompt
- estimated size

## 10. MobileOpportunitySummary

Reduzierte Felder:

- Opportunity ID
- Title
- Company
- Primary Location
- Status
- Assessment Summary
- Availability
- Freshness
- preferred external link indicator

## 11. MobileMapProjection

Wie MapProjection, aber mit reduziertem Preview und ohne administrative Felder.

## 12. DataSnapshotMetadata

- Snapshot ID
- generated at
- Vocation data version
- latest import time
- stale indicator
- supported contracts
