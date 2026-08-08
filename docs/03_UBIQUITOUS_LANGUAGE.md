# Vocation – Ubiquitous Language

**Status:** Draft 0.2

## Zentrale Begriffe

### Job Opportunity

Stabile persönliche Repräsentation einer konkreten beruflichen Möglichkeit. Sie ist die Einheit für Bewertung, Priorisierung, Ausschluss, Gruppierung und Vergleich.

### Job Posting

Konkrete veröffentlichte Darstellung einer Job Opportunity, typischerweise mit Source, Source Reference, Titel und Beschreibung.

### Research Observation

Zeit-, quellen- und prozessgebundene Aussage über ein fachliches Objekt. Sie ist keine zeitlose Wahrheit.

### Source

Fachlicher Ursprung einer Information, etwa Unternehmenskarriereseite oder StepStone.

### Source Reference

Konkreter wiederauffindbarer Verweis innerhalb einer Source, meist URL oder externe ID.

### Research Bundle

Versioniertes Austauschpaket aus dem External Research Context an Vocation. Es ist kein internes Vocation-Domänenmodell.

### Research Prompt

Versionierte, von Vocation erzeugte Anweisung für einen externen Rechercheprozess.

### Prompt Template

Wiederverwendbare Vorlage für einen bestimmten Recherchemodus.

### Prompt Scope

Explizit begrenzter fachlicher Umfang eines Research Prompt, etwa Gesamtbestand, Company, Opportunity oder fehlende Felder.

### Prompt Context Snapshot

Von Vocation erzeugter, read-only Kontextbestand, der in einen Prompt eingebettet oder beigelegt wird. Er enthält nur die für den Scope nötigen Informationen.

### Bundle Version

Version des Research-Bundle-Vertrags.

### Prompt Version

Version des Prompt-Templates und seiner erwarteten Ausgabeanforderungen.

### Import

Kontrollierter Vorgang zur Validierung, Übersetzung und Anwendung eines Research Bundle.

### Import Record

Nachvollziehbarer Datensatz eines Importversuchs.

### Company

Organisation, der eine Job Opportunity zugeordnet ist.

### Organization Unit

Relevanter organisatorischer Teil einer Company, nur bei belastbarer Evidenz.

### Location

Räumlicher Bezugspunkt mit Bedeutung, Herkunft und Precision.

### Work Location

Für eine Opportunity angegebener oder bestätigter Arbeitsort.

### Location Precision

Genauigkeit eines Orts: `exact_address`, `site`, `city`, `region`, `approximate`, `unknown`.

### Assessment

Nachvollziehbare Bewertung mit Ursprung, Zeitpunkt, Methode und Ergebnis.

### External Assessment

Assessment aus dem Research Context.

### Personal Assessment

Vom Nutzer vorgenommene oder bestätigte Bewertung.

### Risk

Klärungsbedürftiger oder negativer Aspekt; noch keine Exclusion.

### Decision

Bewusste persönliche Festlegung.

### Exclusion

Decision, eine Opportunity oder Company nicht weiterzuverfolgen. Sie löscht nichts.

### Tracking Status

Position im persönlichen Sichtungsprozess: `new`, `to_review`, `interesting`, `shortlisted`, `deferred`, `excluded`, `archived`.

### Availability Observation

Zeitbezogene Beobachtung über die Erreichbarkeit oder Aktivität eines Posting.

### Availability

Abgeleitete aktuelle Einschätzung: `available`, `unavailable`, `uncertain`, `unknown`.

### Freshness

Aktualität des vorhandenen Informationsstands, nicht der realen Stelle.

### Possible Duplicate

Dokumentierte Vermutung einer möglichen Identität.

### Duplicate Decision

Explizite Entscheidung: identisch, getrennt, verwandt oder ungeklärt.

### Opportunity Group

Benannte Sammlung für einen organisatorischen Zweck.

### Application Wave

Spezielle Opportunity Group für eine gemeinsame Bewerbungsphase.

### Read Model

Für einen konkreten Lesezweck aufbereitete Sicht ohne eigene fachliche Datenhoheit.

### Map Projection

Read Model, das Vocation-Daten in kartendarstellbare Features übersetzt.

### External Link

Validierte Source Reference, die nach expliziter Nutzeraktion im Standardbrowser geöffnet werden kann.

### Preferred Posting Link

Für eine konkrete Ansicht bevorzugte, aktuell nutzbare Source Reference. Sie bleibt eine Auswahlregel und keine neue fachliche Wahrheit.

### Mobile Projection

Reduziertes Read Model für mobile Nutzung.

## Verbotene oder unpräzise Begriffe

- `Job` ohne Präzisierung
- `Candidate` für eine Stelle
- `Entry` statt fachlicher Objektbezeichnung
- `Deleted Job`
- `Current Data` ohne Zeitpunkt
- `Truth` für abgeleitete Informationen
- `Prompt Result` ohne Unterscheidung zwischen Text und Research Bundle

## Sprachliche Regeln

- Prompt-Erzeugung ist kein Research.
- Import ist kein bloßes JSON-Einlesen.
- Ein Posting-Link ist nicht die Opportunity.
- Ein Karten-Pin ist eine Projektion, kein Domänenobjekt.
- Das Öffnen eines Links ist eine Nutzeraktion, keine automatische Navigation.
## Persönliche Triage (v0.2.0)

Eine **Personal Assessment** gehört Vocation und ist von einem **External Assessment** getrennt. Pro Opportunity und Criterion existiert genau ein aktuelles Personal Assessment. `CreatePersonalAssessment` legt die erste unveränderliche Revision an; `RevisePersonalAssessment` legt eine neue Revision mit Vorgängerreferenz an. Nur die aktuelle Revision darf revidiert werden, ältere Revisionen bleiben sichtbar. Numeric-, Categorical-, Boolean- und Text-Werte werden gegen das Vocation-Kriterium validiert. Create und Revise benötigen ein aktives Opportunity-Kriterium. Sobald ein Criterion durch ein External oder Personal Assessment referenziert wird, sind semantische Änderungen geschützt; Name und Beschreibung dürfen weiter gepflegt werden.

Der **Tracking Status** ist genau einer von `new`, `to_review`, `interesting`, `shortlisted`, `deferred`, `excluded` oder `archived`. Normale nicht ausgeschlossene Status dürfen direkt wechseln; `excluded` ist kein normaler Statuswechsel.

Eine **Exclusion** ist eine eigene, begründete Operation mit nichtleerem Grund und unveränderlichem Decision-Eintrag, der den vorherigen Status speichert. **Restore** ist nur bei aktueller Exclusion zulässig, verweist auf genau diese aktive Exclusion und setzt standardmäßig deren gespeicherten vorherigen Status. Ein expliziter alternativer nicht ausgeschlossener Status ist erlaubt. Exclusion und Restore bleiben historisch erhalten; wiederholte Zyklen referenzieren jeweils die richtige aktive Exclusion.

Research Bundle Imports verändern Tracking Status, Personal Assessments, deren Revisionen und Opportunity Decisions nicht.
