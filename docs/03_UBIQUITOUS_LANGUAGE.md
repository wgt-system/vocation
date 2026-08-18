# Vocation – Ubiquitous Language

**Status:** current through the implemented post-v0.4 profile/fit/research baseline; planned terms are explicitly marked.

## Sprachliche Grundregel

Vocation unterscheidet **fachliche Domain-Begriffe** von **user-facing Produktbezeichnungen**.

Ein stabiler Domain-Begriff wie `OpportunityGroup` darf intern bestehen bleiben, obwohl die Oberfläche später einen verständlicheren Begriff wie Sammlung oder Bewerbungsphase verwendet. UI-Wording ist keine automatische Domain-Migration.

## Zentrale Stellenmarkt-Begriffe

### Job Opportunity

Stabile persönliche Repräsentation einer konkreten beruflichen Möglichkeit. Sie ist die Einheit für Bewertung, Priorisierung, Ausschluss, Gruppierung, Vergleich und ApplicationCase-Bezug.

`Opportunity` ist ein Domain-Begriff. Die deutsche Produktoberfläche muss das englische Wort nicht als Seitentitel anzeigen.

### Job Posting

Konkrete veröffentlichte Darstellung einer Job Opportunity, typischerweise mit Source, Source Reference, Titel und Beschreibung.

### Company

Organisation, der eine Job Opportunity zugeordnet ist.

### Organization Unit

Relevanter organisatorischer Teil einer Company, nur bei belastbarer Evidenz.

### Research Observation

Zeit-, quellen- und prozessgebundene Aussage über ein fachliches Objekt. Sie ist keine zeitlose Wahrheit.

### Source

Fachlicher Ursprung einer Information, etwa Unternehmenskarriereseite, Job Board oder professionelles Netzwerk.

### Source Reference

Konkreter wiederauffindbarer Verweis innerhalb einer Source, meist URL oder externe ID.

## Persönlicher Suchkontext

### Candidate Profile

Private, revisionierte Vocation-Repräsentation von Person-/Qualifikationsfakten, die für Recherche, Fit und künftig Bewerbungsarbeit relevant sein können.

Candidate Profile ist **keine** Suchstrategie und keine Published Capability. Änderungen erzeugen nachvollziehbare Revisionen.

### Search Profile

Vocation-owned, revisionierte Strategie für eine konkrete Jobsuche. Sie beschreibt z. B. Zielrollen, Seniority, Technologien, Search Areas, Arbeitsmodell, Beschäftigungsarten, Branchen, Gehalt, harte Constraints und Evaluation Policy.

Mehrere Search Profiles können dieselben Candidate-Profile-Fakten wiederverwenden. Genau ein Search Profile kann als Default markiert sein.

### Search Area (geplant, #47)

Vocation-owned Bedeutung eines geografischen Suchbereichs innerhalb eines Search Profile. Eine Search Area referenziert einen generisch aufgelösten Ort und kann optional einen Radius tragen.

Der Ort selbst bzw. generisches Place Search/Geocoding ist Orientation-owned. Remote, bundesweite Suche und Relocation sind keine künstlichen Search Areas, sondern eigene Suchpolitiken.

### Search Vocabulary / Catalog Entry (geplant, #48)

Vocation-owned Referenzeintrag für Suchstrategie-Begriffe wie Rolle, Technologie oder Branche. Ein Eintrag kann einen kanonischen Anzeigenamen, Aliases, Status und Gruppierung besitzen.

Custom Terms bleiben möglich. Historische Search-Profile-Revisionen dürfen durch spätere Katalogänderungen nicht umgedeutet werden.

Geografische Orte gehören nicht in diesen Vocation-Katalog.

### Evaluation Policy

Search-Profile-spezifische Regeln zur Bewertung von Assessment Criteria, insbesondere Gewichtung und unterstützte Required-/Minimum-Semantik. Evaluation Policy verändert nicht die globale Bedeutung eines Assessment Criterion.

### Opportunity Fit

Read-only, deterministisch erklärbare Bewertung einer Opportunity gegen eine konkrete Search-Profile-Revision. Fit trennt:

- Hard-Constraint-Status,
- gewichteten Fit Score, wenn genügend Evidenz vorhanden ist,
- Evidence Completeness,
- Criterion Contributions,
- explizit fehlende Evidenz.

Fit mutiert keine Opportunity, Decision, Tracking Status oder ApplicationCase.

## Research und Prompting

### Research Bundle

Versioniertes Austauschpaket aus dem External Research Context an Vocation. Es ist kein internes Vocation-Domänenmodell.

Research Bundle 1.0 bleibt der eingefrorene Initial-Research-Vertrag.

### Research Update Bundle

Separater versionierter Vertrag für kontrollierte Updates eines bekannten Bestands. Version 2.0 verwendet Vocation-issued opaque Correlation References aus einem Prompt Context Snapshot.

### Availability Check Bundle

Separater versionierter Vertrag für append-only Availability Observations bekannter Postings. Er ist keine allgemeine Research-Update-Abkürzung.

### Research Prompt

Versionierte, von Vocation erzeugte Anweisung für einen externen Rechercheprozess.

Prompt-Erzeugung ist kein Research.

### Prompt Template

Wiederverwendbare, versionierte Vorlage für einen bestimmten Recherchemodus.

### Prompt Scope

Explizit begrenzter fachlicher Umfang eines Research Prompt, etwa Gesamtbestand, Company, Opportunity oder fehlende Felder.

### Prompt Context Snapshot

Von Vocation erzeugter read-only Kontextbestand für einen Prompt. Er enthält nur die für den Workflow nötigen Informationen und friert relevante Revisionen/Correlation References für Provenienz ein.

Bei profile-aware Initial Research kann der Snapshot die exakte Search-Profile-Revision und – nach expliziter Auswahl – Candidate-Profile-Revision enthalten, ohne deren interne IDs in Research Bundle 1.0 einzubauen.

### Research Strategy / Research Grind (geplant, #49)

Explizite Methode eines Research Run zur Erhöhung der Marktabdeckung, ohne die Search-Profile-Präferenzen selbst umzudeuten.

Geplante Strategien umfassen role-first, company-first, domain/technology, regional, freshness re-check und gap/coverage grind.

`Grind` ist ein Arbeitsbegriff für einen bewusst abgegrenzten, wiederholbaren Research Run. In der finalen UI kann ein neutralerer deutscher Anzeigename verwendet werden.

### Research Coverage (geplant, #49)

Persistente Information darüber, welche Discovery-Bereiche – insbesondere Companies/Karriereseiten – bereits untersucht wurden, wann und mit welchem Ergebnis/Prompt Run. Coverage ist keine Job Opportunity und kein Beweis, dass eine Stelle existiert.

### Import

Kontrollierter Vorgang zur Validierung, Übersetzung, Scope-/Identitätsprüfung und atomaren Anwendung eines versionierten Bundles.

Import ist kein bloßes JSON-Einlesen.

### Import Record

Nachvollziehbarer Datensatz eines Importversuchs.

### Bundle Version

Version des jeweiligen Research-/Update-/Availability-Vertrags.

### Prompt Version

Version des Prompt-Templates und seiner erwarteten Ausgabeanforderungen.

## Räumliche Begriffe

### Location

Räumlicher Bezugspunkt mit Bedeutung, Herkunft und Precision.

### Work Location

Für eine Opportunity angegebener oder bestätigter Arbeitsort. Work Location ist Research-/Vocation-Fachinformation und nicht dasselbe wie eine Search Area.

### Location Precision

Genauigkeit eines Orts: `exact_address`, `site`, `city`, `region`, `approximate`, `unknown`.

### MapLocationResolution

Vocation-owned Supporting Data für genau eine WorkLocation: Work Location ID, Latitude, Longitude, Resolution Source (`manual` oder `geocoder`), optionaler Provider Key, Zeit und verwendete Query/Label.

Es gibt höchstens eine aktuelle Resolution pro WorkLocation. Resolution ist weder Research Evidence noch Decision History und erhöht nie die Research-Precision einer WorkLocation.

### Map Projection

Internes Vocation-Read-Model mit Features für aufgelöste WorkLocations aus einer expliziten Opportunity-Menge. Die Karte besitzt keine eigene fachliche Datenhoheit.

## Assessments und persönliche Triage

### Assessment

Nachvollziehbare Bewertung mit Ursprung, Zeitpunkt, Methode und Ergebnis.

### External Assessment

Assessment aus dem Research Context.

### Personal Assessment

Vom Nutzer vorgenommene oder bestätigte, Vocation-owned Bewertung. Revisionen bleiben historisch erhalten und werden nicht durch Research überschrieben.

### Risk

Klärungsbedürftiger oder negativer Aspekt; noch keine Exclusion. Eine konkrete universelle Risk-Read-/Scoring-Quelle ist nicht Teil des stabilen Vergleichsmodells.

### Decision

Bewusste persönliche Festlegung.

### Exclusion

Decision, eine Opportunity nicht weiterzuverfolgen. Sie löscht keine Research-Historie.

### Tracking Status

Position im persönlichen Sichtungsprozess: `new`, `to_review`, `interesting`, `shortlisted`, `deferred`, `excluded`, `archived`.

`Tracking Status` ist Domain-/API-Sprache. Die Oberfläche soll konsistente deutsche Anzeigenamen verwenden statt gemischter englisch/deutscher Labels.

### Opportunity Note

Private lokale Notiz zu einer Opportunity. Sie ist weder Assessment noch Research Evidence und beeinflusst Fit nicht automatisch. Research-Imports überschreiben sie nicht.

## Availability und Freshness

### Availability Observation

Zeitbezogene Beobachtung über die Erreichbarkeit/Aktivität eines Posting.

Availability Check Bundle 1.0 verwendet `explicitly_available`, `explicitly_unavailable`, `temporarily_unreachable`, `not_found` und `indeterminate`. Die letzten drei sind unzuverlässige Evidenz und führen zu `uncertain`, niemals automatisch zu `unavailable`.

### Availability

Abgeleitete aktuelle Einschätzung: `available`, `unavailable`, `uncertain`, `unknown`.

Opportunity Availability aggregiert Posting-Evidenz, ohne einen permanenten Opportunity-Closed-Zustand zu erzeugen.

### Freshness

Im implementierten Availability-Slice ausschließlich Alter der Availability-Evidenz. `last_checked_at` ist der Zeitpunkt der neuesten Availability Observation; `age_days` sind verstrichene UTC-24-Stundenperioden.

Freshness ist **nicht** automatisch das Alter aller Research Observations. Ein älteres Posting kann ein Verifikationssignal sein, ist allein aber kein Beweis für Unavailability.

## Identität und Dubletten

### Possible Duplicate

Dokumentierte Vermutung einer möglichen Identität. Sie ist Evidenz und keine Identitätsentscheidung.

### Duplicate Case

Persistierter Review-Fall zwischen zwei möglicherweise identischen/verbundenen Subjects. Er führt keine automatische Zusammenführung durch.

### Duplicate Decision

Explizite persönliche Review-Entscheidung für genau einen Duplicate Case. Erlaubte Outcomes sind `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` und `keep_unresolved`.

Entscheidungen sind append-only. `confirmed_duplicate` klassifiziert nur und führt keinen Merge, keine Löschung und keine Referenzumschreibung aus.

## Organisation und Bewerbungsplanung

### Opportunity Group

Benannte interne Sammlung mit stabiler Group ID, Name, optionaler Beschreibung und Typ `general` oder `application_wave`. Memberships besitzen explizite Reihenfolge; eine Opportunity darf mehreren Groups angehören.

`OpportunityGroup` ist ein Domain-Begriff und muss nicht als `Group` in der deutschen Hauptnavigation erscheinen.

### Application Wave

Spezielle `OpportunityGroup` für eine gemeinsame Bewerbungsphase. Sie ist kein separates Aggregate und bringt keine impliziten Fristen-, Submission- oder Statusänderungen mit.

Die manuelle Produktabnahme hat `Groups/Waves` als literal user-facing Begriff nicht akzeptiert. #45/#50 prüfen verständlichere Präsentationsbegriffe wie Sammlungen/Bewerbungsphasen innerhalb eines `Bewerbungen`-Workspaces, ohne die bestehende Domänensemantik still zu ändern.

## Application Domain

### ApplicationCase

Vocation-owned Aggregate für die Bewerbung auf genau eine Opportunity. ApplicationCase-Lifecycle ist unabhängig vom Opportunity Tracking Status.

### ApplicationCase Lifecycle

V1-Zustände: `draft`, `ready`, `submitted`, `interviewing`, `offer`, `accepted`, `rejected`, `withdrawn`. `accepted`, `rejected`, `withdrawn` sind terminal. Erstellung und jede Lifecycle-Änderung sind explizite Nutzeraktionen; Lifecycle Events bleiben historisch sichtbar.

### ApplicationMaterial

Private, von einem ApplicationCase besessene Material-Metadaten mit stabiler Material ID, ApplicationCase ID, Kind `cv`, `cover_letter` oder `other`, Display Name und Revision.

Material-Revisionen werden historisch geführt. Der tatsächliche unveränderliche Payload einer Revision kann über ein `ApplicationDocument` gespeichert werden; der ältere Satz, Dokumentinhalt sei generell undefiniert, gilt seit den implementierten Document-Slices nicht mehr.

### ApplicationDocument

Privater Vocation-owned Inhalt, der genau einer unveränderlichen ApplicationMaterial-Revision zugeordnet ist. Semantische Metadaten umfassen Document ID, Material ID/Revision, Original-Dateiname, Media Type, Byte Size, SHA-256 und Created At.

V1 erlaubt `application/pdf`, `text/plain` und `text/markdown`. Payload ist immutable; Ersatz erfordert eine neue Material-Revision.

### ApplicationDocumentStore

Provider-neutraler Infrastruktur-Port für private Payload Bytes und opaque Vocation-owned Storage References. Domain/Application kennt keine physischen Pfade, Cloud- oder Conveyance-Details.

### ApplicationDocument Access

Read-only Retrieval des immutable Payloads einer exakt bestimmten Material-Revision nach Integritätsprüfung. Dies ist weder Publication noch Cross-device Export/Sync.

### Career/Profile Document (geplant, #46)

Wiederverwendbares privates Dokument im persönlichen Karriereprofil, etwa CV, Abschlusszeugnis oder Arbeitszeugnis. Es ist nicht auf genau eine Bewerbung beschränkt.

Die geplante Implementierung soll vorhandene Vocation-Dokument-/Integritätsinfrastruktur wiederverwenden, ohne ApplicationMaterial-Ownership semantisch falsch zu verbiegen. Ein Career/Profile Document wird nur explizit einer Anwendung/Prompt-Disclosure zugeordnet.

### Document Extraction Proposal (geplant, #46)

Aus einem privaten Dokument extrahierter Text/Faktvorschlag mit Provenienz. Er ist kein bestätigter Candidate-Profile-Fakt und erzeugt erst nach expliziter Nutzerannahme eine Profiländerung.

### Application Draft (geplant, #50)

Explizit generierter, noch nicht akzeptierter privater Text für eine Bewerbung, z. B. Anschreiben oder Bewerbungsnachricht. Ein externer Modelloutput ist zunächst Draft/Proposal und darf erst durch einen Vocation-Use-Case als ApplicationMaterial-Revision akzeptiert werden.

Application Draft bedeutet niemals automatische Submission.

## Links und Vergleich

### External Link

Abgeleiteter Read-/Application-Wert aus Posting, Source und Source Reference. Es gibt keine eigene ExternalLink-Persistenz.

Die ExternalLinkPolicy akzeptiert ausschließlich absolute `https`-URLs mit nichtleerem Host. Ungültige oder nicht erlaubte Schemes erreichen niemals den Browser Adapter.

### Preferred Posting Link

Deterministisch bevorzugter ExternalLink für eine konkrete Ansicht. Ohne explizite Auswahl gilt die implementierte Ordnung nach Availability, Source Type, `observed_at` und Posting ID. Eine manuelle Auswahl für einen Open-Vorgang wird nicht als persönliche Präferenz persistiert.

### Opportunity Comparison

Read-only interner Vergleich einer temporär ausgewählten, explizit geordneten Menge von 2 bis 4 bestehenden Opportunities. Die Ansicht besitzt keine eigene fachliche Datenhoheit und ist kein zweites Ranking-/Recommendation-System.

## Publication

### Published Read Projection

Client-neutrale, versionierte veröffentlichte Read Projection. Der ältere Begriff `Mobile Projection` ist zu client-spezifisch.

### Published Vocation Capability

Versionierte Capability-/Vertragsgrenze für geeignete Vocation-Daten. `Opportunity Overview` 1.0 und `Published Map Projection` 1.0 sind eingefrorene provider-owned Contracts.

Opaque Refs dürfen Consumer speichern/vergleichen/zurückgeben, aber nicht parsen oder als Datenbankstruktur interpretieren.

### Publication Snapshot

Veröffentlichte, abgeleitete Momentaufnahme einer Read Projection mit Publication Metadata. Ihr Alter beschreibt Publication Age, nicht Posting Availability/Freshness.

## Verbotene oder unpräzise Begriffe

- `Job` ohne Präzisierung, wenn Opportunity/Posting gemeint ist
- `Candidate` für eine Stelle
- `Entry` statt fachlicher Objektbezeichnung
- `Deleted Job`
- `Current Data` ohne Zeitpunkt
- `Truth` für abgeleitete Informationen
- `Prompt Result` ohne Unterscheidung zwischen Text und versioniertem Bundle
- `PDF Reader Service` als Architekturentscheidung nur weil PDF-Dateien gelesen werden sollen

## Sprachliche Regeln

- Prompt-Erzeugung ist kein Research.
- Import ist kein bloßes JSON-Einlesen.
- Ein Posting-Link ist nicht die Opportunity.
- Ein Karten-Pin ist eine Projektion, kein Domänenobjekt.
- Das Öffnen eines Links ist eine Nutzeraktion, keine automatische Navigation.
- Ein `confirmed_duplicate` ist kein Merge.
- Candidate Profile ist keine Search Strategy.
- Search Area ist keine Work Location.
- Research Coverage ist kein Beweis für eine Opportunity.
- Ein externer Research-/Extraction-/Generation-Output ist kein bestätigter privater Vocation-Fakt.
- Interne englische Domain-Terme müssen nicht literal als gemischte UI-Texte erscheinen.

## Persönliche Triage – Invarianten

Pro Opportunity und Criterion existiert genau ein aktuelles Personal Assessment. Änderungen erzeugen explizite immutable Revisionen; ältere Revisionen bleiben sichtbar. Research Bundle Imports verändern Tracking Status, Personal Assessments, deren Revisionen, Opportunity Decisions oder private Opportunity Notes nicht.

`excluded` wird über eine begründete Exclusion-Operation erzeugt und über Restore aufgehoben; historische Decisions bleiben erhalten.

## Produkt-Acceptance-Hinweis

Die erste manuelle Produktabnahme des post-v0.4-`dev`-Stands hat vor allem Presentation-/Workflow-Probleme aufgedeckt. Die fachlichen Begriffe oben bleiben dadurch nicht automatisch falsch. Die aktuell akzeptierte UI-/Produkt-Richtung und die explizit geplanten Begriffe stehen in `17_MANUAL_PRODUCT_ACCEPTANCE.md` und den Issues #45–#50.
