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

Availability Check Bundle 1.0 verwendet ausschließlich `explicitly_available`, `explicitly_unavailable`, `temporarily_unreachable`, `not_found` und `indeterminate`. Die letzten drei Ergebnisse sind unzuverlässige Evidenz und führen zu `uncertain`, niemals automatisch zu `unavailable`.

### Availability

Abgeleitete aktuelle Einschätzung: `available`, `unavailable`, `uncertain`, `unknown`.

Die Ableitung verwendet die neueste Availability Observation: explizit verfügbar → `available`, explizit nicht verfügbar → `unavailable`, temporär unerreichbar/nicht gefunden/indeterminiert → `uncertain`, keine Observation → `unknown`. Opportunity Availability aggregiert ihre Postings, ohne einen permanenten Opportunity-Closed-Zustand zu erzeugen.

### Freshness

In Slice 9 ausschließlich Freshness der Availability-Evidenz. `last_checked_at` ist der Zeitstempel der neuesten Availability Observation; `age_days` sind ganze verstrichene UTC-24-Stundenperioden aus einer injizierten Uhr. Es gibt keine Schwellenkategorien oder automatische Ablaufregel. Dies ist nicht Freshness von Gehalt, Technologien, Aufgaben, Arbeitsmodell, Assessments oder allgemeinen Observations.

### Possible Duplicate

Dokumentierte Vermutung einer möglichen Identität.

### Duplicate Decision

Explizite Entscheidung: identisch, getrennt, verwandt oder ungeklärt.

### Opportunity Group

Benannte Sammlung für einen organisatorischen Zweck mit stabiler Group ID, nichtleerem Namen, optionaler Beschreibung und Typ `general` oder `application_wave`. Memberships referenzieren Group ID und Opportunity ID sowie eine explizite Position. `(group_id, opportunity_id)` ist eindeutig; eine Opportunity darf mehreren Groups angehören.

### Application Wave

Spezielle `OpportunityGroup` für eine gemeinsame Bewerbungsphase. Sie ist in V1 kein separates Aggregate und bringt keine impliziten Bewerbungs-, Fristen- oder Statussemantiken mit.

### Read Model

Für einen konkreten Lesezweck aufbereitete Sicht ohne eigene fachliche Datenhoheit.

### Map Projection

Internes Vocation-Read-Model mit genau einem Feature pro aufgelöster WorkLocation. Die Projektion wird aus einer expliziten Menge von Opportunity IDs gebildet und verwendet damit dasselbe Filterergebnis wie die Opportunity-Liste.

### MapLocationResolution

Vocation-owned supporting data für genau eine WorkLocation: `work_location_id`, Latitude, Longitude, `resolution_source` (`manual` oder `geocoder`), optionaler `provider_key`, `resolved_at` und die für die Auflösung verwendete Query oder das Label. Latitude liegt zwischen -90 und 90, Longitude zwischen -180 und 180. Es gibt höchstens eine aktuelle Resolution pro WorkLocation. Eine erfolgreiche explizite Neuauflösung darf die bisherige abgeleitete Resolution ersetzen.

MapLocationResolution ist weder Research Evidence noch Decision History. Ohne Resolution ist eine WorkLocation `unmapped`, nicht ungültig. Geocoding darf die WorkLocation Precision nie erhöhen; die angezeigte Precision bleibt die der WorkLocation. Provider bleiben hinter einem provider-neutralen Port und sind kein Domain- oder Published-Contract-Bestandteil.

### External Link

Validierte Source Reference, die nach expliziter Nutzeraktion im Standardbrowser geöffnet werden kann.

### Preferred Posting Link

Für eine konkrete Ansicht bevorzugte, aktuell nutzbare Source Reference. Sie bleibt eine Auswahlregel und keine neue fachliche Wahrheit.

### Published Read Projection

Aktueller client-neutraler Begriff für eine veröffentlichte Read Projection. `Mobile Projection` ist der veraltete client-spezifische Begriff.

### Published Vocation Capability

Versionierte Capability-/Vertragsgrenze für geeignete Vocation-Daten. Die erste geplante Capability ist `Opportunity Overview` 1.0.

Der Published Contract 1.0 ist durch `schemas/published-opportunity-overview-v1.schema.json` kanonisch definiert. `opportunity_ref` und `company_ref` sind stabile opaque, von Vocation ausgestellte Referenzen. Verbraucher dürfen sie speichern, vergleichen und zurückgeben, aber weder parsen noch Datenbankstrukturen daraus ableiten.

### Publication Snapshot

Eine veröffentlichte, abgeleitete Momentaufnahme einer Read Projection mit Publication Metadata. Ihr Alter beschreibt Publication Age, nicht die Freshness oder Availability eines Job Postings.

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
