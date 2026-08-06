# Vocation – Research Bundle Import Contract

**Status:** Draft 0.1  
**Current Bundle Version:** `1.0`

## 1. Zweck

Das Research Bundle ist die versionierte Published Language zwischen External Research Context und Vocation.

Es ist:

- JSON,
- vollständig schema-validierbar,
- unabhängig vom internen Datenbankmodell,
- für Initial- und Update-Recherche geeignet,
- quellen- und zeitbezogen,
- frei von Vocation-internen Personal Decisions.

## 2. Top-Level-Struktur

```json
{
  "bundle_version": "1.0",
  "bundle_id": "uuid-or-stable-id",
  "generated_at": "2026-08-06T17:00:00Z",
  "research_scope": {},
  "sources": [],
  "companies": [],
  "opportunities": [],
  "postings": [],
  "observations": [],
  "assessments": [],
  "warnings": []
}
```

## 3. Research Scope

```json
{
  "type": "initial_market_research",
  "requested_vocation_ids": [],
  "requested_fields": [],
  "as_of_date": "2026-08-06"
}
```

Erlaubte Types:

- `initial_market_research`
- `full_update`
- `company_update`
- `opportunity_update`
- `gap_filling`
- `availability_check`
- `custom_subset`

## 4. IDs

Externe Bundle-IDs sind nur innerhalb des Bundles oder Research Context stabil. Sie werden nicht als interne Vocation IDs übernommen.

Update-Bundles dürfen bekannte Vocation IDs als Referenz enthalten:

```json
{
  "vocation_opportunity_id": "optional-known-id"
}
```

Diese Referenz ist ein Hinweis und wird validiert.

## 5. Sources

Pflicht:

- external source ID
- name
- source type

Optional:

- base URL
- notes

## 6. Companies

Pflicht:

- external company ID
- canonical name

Optional:

- alternative names
- official website
- locations
- known Vocation Company ID

## 7. Opportunities

Beschreiben recherchierte berufliche Möglichkeiten.

Pflicht:

- external opportunity ID
- company reference
- canonical title proposal

Optional:

- known Vocation Opportunity ID
- organization unit
- work locations
- suggested relationships
- scope notes

## 8. Postings

Pflicht:

- external posting ID
- source reference
- title
- observed at

Optional:

- URL
- external platform ID
- published at
- opportunity reference
- availability observation
- content fingerprint

URL-Regeln:

- nur `https` oder `http`,
- keine ausführbaren oder lokalen Schemes,
- URL darf fehlen, wenn eine andere Source Reference existiert.

## 9. Observations

Pflicht:

- external observation ID
- subject reference
- observation type
- observed value
- observed at
- source reference

Optional:

- confidence
- evidence excerpt
- research method

## 10. Assessments

Nur externe Assessments.

Pflicht:

- external assessment ID
- subject reference
- assessment type
- origin = `external_research`
- created at

Optional:

- dimensions
- score and scale
- reasoning
- risks

Verboten:

- Personal Assessment
- Exclusion Decision
- Tracking Status Change
- Application Wave Membership

## 11. Update-Regeln

Ein Update Bundle:

- muss seinen Scope benennen,
- soll bekannte Vocation IDs referenzieren, wenn vorhanden,
- muss nur neue oder geänderte Observations liefern,
- darf geschützte Personal Decisions nicht verändern,
- darf außerhalb des Scopes liegende Informationen höchstens als Warning liefern.

## 12. Importstrategie Version 1

Version 1 verwendet bevorzugt einen atomaren Bundle-Import:

- alle blockierenden Fehler verhindern die Anwendung,
- Warnungen verhindern den Import nicht,
- Entry-Fehler sind blockierend, solange partieller Import nicht ausdrücklich eingeführt wird.

## 13. Fingerprint und Idempotenz

Der Fingerprint wird aus normalisiertem Bundle-Inhalt berechnet.

Ein identischer Fingerprint:

- wird nicht erneut angewendet,
- verweist auf den bestehenden Import Record,
- kann erneut validiert, aber nicht doppelt geschrieben werden.

## 14. Fehlerklassen

- `UNSUPPORTED_BUNDLE_VERSION`
- `INVALID_JSON`
- `SCHEMA_VALIDATION_FAILED`
- `UNKNOWN_REFERENCE`
- `INVALID_DATE`
- `INVALID_URL`
- `SCOPE_VIOLATION`
- `PROTECTED_FIELD_ATTEMPT`
- `DUPLICATE_EXTERNAL_ID`
- `IMPORT_ALREADY_APPLIED`

## 15. Schema

Das verbindliche technische Schema liegt unter:

`schemas/research-bundle-v1.schema.json`

## 16. Beispiele

- `examples/imports/initial-valid.json`
- `examples/imports/update-valid.json`
- `examples/imports/invalid-protected-decision.json`
