# Vocation – Research Bundle Import Contract

**Status:** Version 1.0 für den ersten Meilenstein
**Current Bundle Version:** `1.0`

## 1. Zweck und Geltungsbereich

Das Research Bundle ist die versionierte Published Language zwischen External Research Context und Vocation. Der erste Meilenstein importiert ausschließlich `initial_market_research`. Update-Bundles bleiben ein späterer Slice.

Das Bundle ist vollständig schema- und fachlich validierbar, unabhängig vom internen Datenbankmodell, quellen- und zeitbezogen und frei von persönlichen Vocation-Zuständen.

Das verbindliche Schema ist `schemas/research-bundle-v1.schema.json`. Alle definierten Vertragsobjekte sind geschlossen. Unbekannte Properties sind Blocker und werden niemals automatisch zu Domänenfeldern oder Assessment-Kriterien.

## 2. Top-Level-Struktur

```json
{
  "bundle_version": "1.0",
  "bundle_id": "research-run-001",
  "generated_at": "2026-08-06T17:00:00Z",
  "research_scope": {
    "type": "initial_market_research",
    "as_of_date": "2026-08-06",
    "search_profile": "Junior software roles",
    "constraints": ["Hamburg or remote"]
  },
  "sources": [],
  "source_references": [],
  "companies": [],
  "opportunities": [],
  "postings": [],
  "observations": [],
  "assessments": [],
  "warnings": []
}
```

## 3. IDs und Referenzen

- `id`-Felder sind nichtleere bundle-lokale IDs und innerhalb ihrer Collection eindeutig.
- Referenzen innerhalb des Bundles müssen auf ein Objekt der erwarteten Collection zeigen.
- Interne Vocation-IDs werden ausschließlich von Vocation erzeugt und erscheinen nicht im Research Bundle.
- Ein Bundle darf keine persönlichen Assessments, Decisions, Tracking Status, Groups oder andere geschützte Properties enthalten.

## 4. Sources und Source References

Eine Source beschreibt den fachlichen Ursprung, etwa eine Company-Careers-Seite. Eine Source Reference ist der konkrete wiederauffindbare Beleg.

Jede Source Reference enthält eine bundle-lokale ID, Source ID, absolute `https`-URL und einen Beobachtungszeitpunkt. Eine externe Referenz-ID und ein Display Label sind optional.

Nur Source-Reference-URLs können später als Originalanzeige geöffnet werden. Relative, nicht-HTTPS oder syntaktisch ungültige URLs sind Blocker. Import und Darstellung öffnen keine URL.

## 5. Companies und Opportunities

Companies und Opportunities enthalten bundle-lokale Identitätsvorschläge und Provenienz:

- Company: Canonical Name, Source Reference, observed at, optional Evidence Summary.
- Opportunity: Company Reference, Canonical Title, Source Reference, observed at, optionale strukturierte Work Locations.

Work Locations besitzen eine definierte Precision und eigene Provenienz. Sie enthalten im ersten Meilenstein Ortsbeschreibung, jedoch noch keine Kartenkoordinaten.

## 6. Postings und Identität

Ein Posting referenziert genau eine Company, eine Opportunity und eine Source Reference. Company und Posting müssen zur Company der Opportunity passen.

1. Vocation erzeugt interne IDs.
2. Bundle-IDs gelten nur innerhalb des Bundles.
3. `Source + external_posting_id` ist der bevorzugte stabile Posting Key.
4. Ohne externe Posting-ID dient die normalisierte kanonische HTTPS-URL als stabiler Key.
5. Widersprechen externe Posting-ID und URL einer bekannten Zuordnung, wird das gesamte Bundle abgelehnt.
6. Es gibt kein fuzzy Matching und keinen automatischen Merge unsicherer Treffer.

## 7. Observations

Eine Observation enthält Subject Type und bundle-lokale Subject ID, kontrollierten Observation Type, typisierten Wert, Source Reference, Beobachtungszeitpunkt sowie optional Confidence und Evidence Summary.

Im ersten Meilenstein sind `technology_requirement`, `task`, `seniority`, `experience_requirement`, `work_model` und `salary` erlaubt.

## 8. External Assessments

Assessments stammen ausschließlich aus `external_research`. Jedes Assessment referenziert ein Company-, Opportunity- oder Posting-Subject, eine Vocation-eigene Criterion ID, einen passenden Wert, mindestens eine Source Reference, einen Erstellungszeitpunkt und optional Reasoning.

Nur aktive, bekannte Kriterien mit passendem Subject Type dürfen importiert werden. Ein unbekanntes Kriterium ist ein Blocker. Externe Assessments verändern keine persönlichen Daten.

## 9. Strukturelle und semantische Validierung

Vor einer Anwendung werden mindestens geprüft:

- JSON-Syntax, Bundle Version und JSON Schema einschließlich Formats,
- eindeutige bundle-lokale IDs,
- vollständige und typkorrekte Referenzen,
- bekannte aktive Assessment-Kriterien und passende Werte,
- erlaubte Subject Types und Observation Types,
- absolute HTTPS Source References,
- gültige Datums- und Zeitwerte,
- Company-/Opportunity-/Posting-Konsistenz,
- deterministische Posting-Identität,
- Abwesenheit unbekannter und geschützter Felder.

## 10. Atomarer Import

Version 1 importiert ein Bundle vollständig atomar:

- Jeder Blocker verhindert alle fachlichen Änderungen.
- Alle Blocker werden im Import Report ausgegeben.
- Warnungen verhindern den Import nicht.
- Partielle Imports sind nicht erlaubt.
- Ein abgelehnter Importversuch kann mit seinen Issues in einer getrennten Protokolltransaktion gespeichert werden.

## 11. Fingerprint und Idempotenz

Der Fingerprint ist SHA-256 über eine kanonische UTF-8-JSON-Darstellung mit rekursiv sortierten Object Keys, kompakten Separatoren und unveränderter Array-Reihenfolge. Whitespace und Object-Key-Reihenfolge beeinflussen den Fingerprint nicht.

Ein bereits erfolgreich angewendeter Fingerprint wird nicht erneut geschrieben und verweist auf den bestehenden Import Record.

## 12. Fehlercodes

- `INVALID_JSON`
- `UNSUPPORTED_BUNDLE_VERSION`
- `SCHEMA_VALIDATION_FAILED`
- `DUPLICATE_BUNDLE_ID`
- `UNKNOWN_REFERENCE`
- `INVALID_DATE`
- `INVALID_URL`
- `UNKNOWN_ASSESSMENT_CRITERION`
- `INVALID_ASSESSMENT_VALUE`
- `SUBJECT_TYPE_MISMATCH`
- `PROTECTED_FIELD_ATTEMPT`
- `IDENTITY_CONFLICT`
- `IMPORT_ALREADY_APPLIED`

## 13. Beispiele

- `examples/imports/initial-valid.json`
- `examples/imports/invalid-nested-property.json`
- `examples/imports/invalid-protected-decision.json`
