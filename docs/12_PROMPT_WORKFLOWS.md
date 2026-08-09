# Vocation – Prompt Workflows

**Status:** Draft 0.1

## 1. Ziel

Vocation standardisiert die Zusammenarbeit mit ChatGPT, ohne eine direkte LLM-API aufzurufen.

Der Nutzer kopiert einen von Vocation erzeugten Prompt in den Chat und importiert anschließend das erzeugte JSON.

## 2. Workflow-Typen

### Initial Market Research

Für einen leeren oder neuen Marktbereich.

Input:

- Suchprofil
- Region
- Technologien
- Ausschlüsse
- gewünschte Anzahl oder Quellen
- Stichtag

Output:

- vollständiges Research Bundle `1.0`

### Full Update

Für den gesamten bekannten Bestand.

Input:

- ein Vocation-erzeugter Prompt Context Snapshot mit opaque Correlation References
- letzte Observations
- bekannte Sources
- offene Duplicate Cases

Output: Research Update Bundle `2.0`; neue Subjects und Scope-Regeln hängen vom gewählten Update-Typ ab. Availability/Freshness ist nicht Teil dieses Vertrags.

### Company Update

Scope: eine oder mehrere Companies.

### Opportunity Update

Scope: vom Nutzer ausgewählte Opportunities; deren Postings sind als Nachfahren im Scope. Eine direkte Posting-Auswahl gehört nicht zu diesem Modus.

### Gap Filling

Scope: fehlende Felder, Widersprüche oder offene Risiken.

### Availability Check (späteres Slice, außerhalb v0.3)

Scope: nur Erreichbarkeit und Verfügbarkeitsbeobachtungen.

## 3. Prompt-Paket

Ein generiertes Prompt-Paket enthält:

1. klare Aufgabe,
2. Scope,
3. Stichtag,
4. Vocation-issued opaque Correlation References für Update Subjects,
5. generische Schutzregeln für persönlichen Zustand,
6. offene Fragen,
7. Rechercheanforderungen,
8. Ausgabe-Schema,
9. Regel „nur JSON“,
10. Bundle Version.

Der Output Contract wird vollständig in den gerenderten Prompt eingebettet. Ein Prompt darf nicht auf lokale Repository-Pfade verweisen. Initial Research enthält außerdem den Snapshot aller zu diesem Zeitpunkt aktiven Vocation Assessment Criteria einschließlich Value Type, erlaubter Skala/Werte und Applicable Subject Type.

## 4. Prompt-Kontext minimieren

Nur für den Scope benötigte Daten werden eingebettet.

Nicht automatisch enthalten:

- vollständige Historie aller Opportunities,
- irrelevante persönliche Notizen,
- Daten anderer Companies,
- technische Datenbankfelder.

## 5. Geschützte Informationen

Persönliche Assessments, Decisions und Tracking Status sowie deren Werte sind im v0.3 nicht Bestandteil des öffentlichen Prompt Context. Templates verwenden stattdessen generische Schutzregeln:

```text
Research-Ausgaben dürfen niemals Personal Assessments, Decisions, Exclusion/Restore oder Tracking Status ausgeben oder mutieren.
```

## 6. Einheitliche Ausgabe

Jeder Prompt verlangt:

- valides JSON,
- keine Markdown-Fences,
- keine Einleitung,
- `bundle_version: "1.0"` nur für `initial_market_research`; Update-Prompts verlangen `bundle_version: "2.0"` und `prompt_context_ref`,
- expliziten Research Scope,
- Quellen und Zeitpunkte,
- keine internen Vocation-IDs und keine erfundenen Correlation References,
- keine unbekannten Properties oder Assessment Criteria,
- vollständige Source References und Provenienz.

## 7. Update-Prompt-Regeln

- bekannte Daten nicht vollständig wiederholen, wenn unverändert,
- Änderungen und neue Observations priorisieren,
- Unsicherheit ausdrücklich markieren,
- nicht erreichbare Quellen nicht automatisch als endgültig geschlossen interpretieren,
- Scope nicht überschreiten.
- Correlation References nur aus dem aktuellen Prompt Context Snapshot echoen.
- Personal Assessments, Tracking Status, Decisions, Exclusions/Restore und Groups/Waves niemals ausgeben.
- Gap Filling darf nur angeforderte Observations oder aktive Criteria liefern und keine neuen Subjects oder Possible Duplicates.

## 8. UI-Anforderungen

Die aktuelle Desktop-UI bietet:

- Prompt-Typ wählen,
- Scope grafisch auswählen,
- Preview,
- Copy to Clipboard und Save,
- Inline-Import des zurückgegebenen JSON,
- Bundle-/Prompt-Versionen und bei Updates die Prompt Context Ref anzeigen.

Ein Prompt-Run-History-Browser ist nicht Bestandteil von v0.3.

## 9. Templates

Verbindliche Vorlagen:

- `prompts/initial-research.md`
- `prompts/full-update.md`
- `prompts/company-update.md`
- `prompts/opportunity-update.md`
- `prompts/gap-filling.md`
- `prompts/availability-check.md` (späteres Slice, nicht v0.3)
- `prompts/output-contract.md`

## 10. Datenschutz und Sicherheit

- kein automatisches Senden,
- Nutzer entscheidet, was kopiert wird,
- keine Secrets,
- keine lokalen Dateipfade,
- Prompt Preview vor Copy,
- Der v0.3 Update Prompt Context enthält keine Personal Assessment-, Decision- oder Tracking-Status-Werte.
