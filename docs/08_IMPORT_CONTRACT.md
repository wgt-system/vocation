# Vocation – Research Bundle Import Contract

**Status:** Zwei implementierte veröffentlichte Research-Verträge auf `dev`
**Initial Bundle Version:** `1.0` (Initial Research)
**Update Bundle Version:** `2.0` (Research Update)

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

## 14. Research Update Bundle 2.0 (v0.3 implemented on `dev`)

Research Bundle `1.0` bleibt unverändert, gültig ausschließlich für `initial_market_research`. Updates verwenden `schemas/research-update-bundle-v2.schema.json` und enthalten zusätzlich den verpflichtenden `prompt_context_ref`. Die Top-Level-Struktur enthält `bundle_version`, `bundle_id`, `generated_at`, `prompt_context_ref`, `research_scope`, `sources`, `source_references`, `companies`, `opportunities`, `postings`, `observations`, `assessments`, `possible_duplicates` und `warnings`; alle Objekte sind geschlossen.

Correlation References werden ausschließlich von Vocation im Prompt Context Snapshot erzeugt. Sie sind opaque, nur für diesen Snapshot gültig, enthalten keine internen ID-Semantiken und dürfen von Research nur echoed werden. Bundle-lokale IDs bleiben die einzigen Referenzen innerhalb des Bundles. Bekannte Subjects enthalten Correlation Reference und nötige bundle-lokale Beziehungs-IDs; neue Subjects haben keine Correlation Reference und müssen die normalen Creation-/Evidence-Felder liefern.

`research_scope.type` ist genau einer von `full_update`, `company_update`, `opportunity_update` oder `gap_filling`. Full Update erlaubt neue Companies, Opportunities und Postings. Company Update erlaubt neue Opportunities/Postings unter ausgewählten Companies, aber keine neuen Companies. Opportunity Update erlaubt neue Postings unter ausgewählten Opportunities; Companies sind nur Kontext, neue Companies und Opportunities sind verboten. Gap Filling erlaubt ausschließlich ausdrücklich angeforderte Subject-/Feld-Ergebnisse, keine neuen Subjects und keine `possible_duplicates`. Scope-Prüfung erfolgt vor jeder Domain-Mutation.

Gap Filling beschränkt sich auf `technology_requirement`, `task`, `seniority`, `experience_requirement`, `work_model`, `salary` und ausdrücklich angeforderte aktive Assessment Criteria. Es verändert nie Identität, Ownership, Work Locations, Availability/Freshness, Personal Assessments, Decisions oder Tracking Status.

Posting-Identität bleibt deterministisch: Source plus `external_posting_id`, sonst die normalisierte HTTPS-URL der referenzierten Source Reference. Ein bekanntes Posting darf optional `identity_evidence` mit verpflichtender `source_reference_id` und optionaler `external_posting_id` enthalten; ein unabhängiges `canonical_url`-Feld gibt es im Update Contract nicht. Diese Evidence dient nur dem späteren Vergleich mit der Correlation Reference. Widerspruch ist `IDENTITY_CONFLICT`; ein Treffer außerhalb des Scopes ist `SCOPE_VIOLATION`. Gap Filling darf keine Posting-Identity-Evidence enthalten. Fuzzy Matching und Merge sind ausgeschlossen.

`possible_duplicates` ist ausschließlich Evidenz für Opportunity- oder Posting-Paare mit unterschiedlichen bundle-lokalen IDs, mindestens einer Source Reference, Evidence Summary und optionaler Confidence. Es bestätigt keine Dublette und löst keinen Merge aus; Company-Duplicates sind nicht enthalten. Update-Blocker sind `UNKNOWN_PROMPT_CONTEXT`, `SCOPE_MISMATCH`, `UNKNOWN_CORRELATION_REFERENCE`, `SCOPE_VIOLATION`, `IDENTITY_CONFLICT` und `INVALID_DUPLICATE_EVIDENCE` neben den bestehenden Schema-/Protected-Field-Fehlern. Jeder Blocker lehnt das vollständige Update vor Domain-Mutation ab.

Version Dispatch ist explizit: `1.0` wird als Initial Research Bundle validiert, `2.0` als Update Bundle gegen den gespeicherten Prompt Context. Planner-Blocker werden vor jeder Domain-Mutation festgestellt; ein akzeptiertes Update wird in genau einer atomaren Apply-Transaktion ausgeführt. Update-Sources und Source References sind neue Provenance-Datensätze. Wiederverwendete Company-, Opportunity- und Posting-Subjects werden nicht kanonisch umgeschrieben. Duplicate Cases werden nur erstellt oder wiederverwendet; es gibt keinen Merge.

Die Bundle-Version `2.0`, der Update-Importer und die vier Update-Prompt-Modi sind auf `dev` implementiert. Die Desktop-Bedienung umfasst Auswahl, Generierung, Preview, Copy/Save und Inline-Import mit Import Report.

Traceability: Ein angewandter Initial-Import persistiert Bundle Version `1.0` ohne Prompt Context Ref. Ein angewandter Update-Import persistiert Bundle Version `2.0` zusammen mit seiner validierten `prompt_context_ref`. Ein identischer Import Report bewahrt die ursprünglichen Import- und Prompt-Metadaten.

Beispiele: `examples/updates/`; Contract Tests: `backend/tests/test_update_bundle_contract.py`.
