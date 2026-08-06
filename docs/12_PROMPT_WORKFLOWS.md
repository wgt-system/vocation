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

- bestehende Opportunity- und Posting-IDs
- letzte Observations
- Freshness
- bekannte Sources
- offene Duplicate Cases
- geschützte Personal Decisions

Output:

- nur neue oder geänderte Observations
- neue Opportunities
- Availability Updates
- keine Änderung persönlicher Decisions

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
- `bundle_version: "1.0"`,
- expliziten Research Scope,
- Quellen und Zeitpunkte,
- keine erfundenen Vocation-IDs.

## 7. Update-Prompt-Regeln

- bekannte Daten nicht vollständig wiederholen, wenn unverändert,
- Änderungen und neue Observations priorisieren,
- Unsicherheit ausdrücklich markieren,
- nicht erreichbare Quellen nicht automatisch als endgültig geschlossen interpretieren,
- Scope nicht überschreiten.

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
