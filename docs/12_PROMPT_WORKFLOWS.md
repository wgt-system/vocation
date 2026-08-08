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
- Freshness
- bekannte Sources
- offene Duplicate Cases
- geschützte Personal Decisions

Output: Research Update Bundle `2.0`; neue Subjects und Scope-Regeln hängen vom gewählten Update-Typ ab. Availability/Freshness ist nicht Teil dieses Vertrags.

### Company Update

Scope: eine oder mehrere Companies.

### Opportunity Update

Scope: ausgewählte Opportunities oder Postings.

### Gap Filling

Scope: fehlende Felder, Widersprüche oder offene Risiken.

### Availability Check

Scope: nur Erreichbarkeit und Verfügbarkeitsbeobachtungen.

## 3. Prompt-Paket

Ein generiertes Prompt-Paket enthält:

1. klare Aufgabe,
2. Scope,
3. Stichtag,
4. bestehende IDs,
5. geschützte Daten,
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

Der Prompt kann persönliche Decisions als Kontext nennen, aber die Ausgabe darf sie nicht ändern.

Beispiel:

```text
Die Opportunity ist persönlich ausgeschlossen. Prüfe nur neue externe Fakten.
Gib keine Änderung des Tracking Status oder der Exclusion aus.
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

Vocation soll anbieten:

- Prompt-Typ wählen,
- Scope grafisch auswählen,
- Preview,
- Copy to Clipboard,
- gespeicherte Prompt Runs,
- Import einem Prompt Run zuordnen,
- Prompt-Template-Version anzeigen.

## 9. Templates

Verbindliche Vorlagen:

- `prompts/initial-research.md`
- `prompts/full-update.md`
- `prompts/company-update.md`
- `prompts/opportunity-update.md`
- `prompts/gap-filling.md`
- `prompts/availability-check.md`
- `prompts/output-contract.md`

## 10. Datenschutz und Sicherheit

- kein automatisches Senden,
- Nutzer entscheidet, was kopiert wird,
- keine Secrets,
- keine lokalen Dateipfade,
- Prompt Preview vor Copy,
- geschützte persönliche Daten nur bei fachlicher Notwendigkeit.
