# Vocation – Domain Vision

**Status:** v0.4.0 is the stable standalone baseline; post-v0.4 technical acceptance is implemented on `dev`; manual product acceptance is blocked.  
**Purpose:** Fachliche Leitlinie für die Entwicklung von Vocation

## 1. Produktvision

Vocation ist eine eigenständig nutzbare, local-first Anwendung für einen persönlichen Stellenmarkt. Sie unterstützt den Nutzer dabei, externe Stellenrecherche in einen strukturierten, nachvollziehbaren und dauerhaft nutzbaren Arbeitsbestand zu überführen, persönliche Suchstrategien wiederzuverwenden, Stellen erklärbar zu bewerten und Bewerbungen vorzubereiten.

Die eigentliche Web-/Marktrecherche findet weiterhin außerhalb von Vocation statt, zunächst insbesondere mithilfe eines externen research-fähigen Modells/Tools. Vocation unterstützt diesen Ablauf durch versionierte Prompt- und Importgrenzen für:

- initiale Recherche mit persistentem Search Profile und optionalem Candidate Profile,
- Aktualisierung eines bestehenden Bestands,
- Aktualisierung ausgewählter Unternehmen oder Stellen,
- Nachrecherche fehlender oder widersprüchlicher Evidenz,
- Availability/Freshness-Prüfung bekannter Postings,
- schema-konforme versionierte Research-/Update-/Availability-Bundles.

Vocation übernimmt externe Ergebnisse erst nach Validierung und kontrollierter Übersetzung. Externe Research-Ausgabe ist keine Vocation-Wahrheit und darf persönliche Vocation-Zustände nicht still überschreiben.

## 2. Fachliches Problem

Ein persönlicher Stellenmarkt besteht nicht nur aus Links. Für belastbare Entscheidungen müssen gemeinsam betrachtet werden:

- konkrete berufliche Möglichkeit,
- veröffentlichte Anzeigen und Quellen,
- Unternehmen, Team und Arbeitsort,
- Technologien und Aufgaben,
- Junior-/Entry-Eignung und Erfahrungsanforderungen,
- Veröffentlichungs-, Recherche- und Prüfzeitpunkte,
- Verfügbarkeit und Aktualität der Availability-Evidenz,
- externe und persönliche Bewertungen,
- persönliche Suchstrategie, harte Anforderungen und weiche Prioritäten,
- Risiken, Ausschlüsse und Entscheidungen,
- Sammlungen/Bewerbungsphasen,
- räumliche Verteilung,
- Originalanzeige und aktiver Bewerbungsweg,
- Bewerbungsfall, Materialien und private Dokumente.

Chats können diese Informationen analysieren, aber schlecht dauerhaft, reproduzierbar und über mehrere Suchläufe hinweg pflegen. Vocation überführt sie in einen strukturierten Bestand mit expliziter Provenienz und persistentem persönlichem Kontext.

## 3. Zielnutzer

Vocation wird zunächst für einen einzelnen Nutzer entwickelt. Es ist kein allgemeines Recruiting-Portal, kein Arbeitgeber-ATS und kein automatisches Bewerbungsversand-System.

Der Nutzer soll persönliche Daten, Search Profiles und Dokumente lokal dauerhaft pflegen können, ohne sie für jeden Recherche- oder Bewerbungsdurchlauf neu einzugeben.

## 4. Zentrale fachliche Fähigkeit

> Extern recherchierte Stelleninformationen und privaten Such-/Bewerbungskontext kontrolliert in einen nachvollziehbaren, vergleichbaren und dauerhaft nutzbaren persönlichen Stellen- und Bewerbungsbestand überführen.

Dazu gehören:

1. Candidate Profile und mehrere Search Profiles persistent/revisioniert pflegen,
2. standardisierte, kontext- und profilbewusste Rechercheprompts erzeugen,
3. versionierte Research-/Update-/Availability-Bundles importieren,
4. Format, Scope, Identität und fachliche Konsistenz prüfen,
5. Job Opportunities, Job Postings, Sources und Observations zuordnen,
6. aktuelle und historische Informationen unterscheiden,
7. persönliche und externe Bewertungen/Entscheidungen trennen,
8. Opportunities erklärbar gegen ein Search Profile bewerten,
9. Bestände suchen, filtern, gruppieren und vergleichen,
10. räumliche Zusammenhänge sichtbar machen,
11. Originalanzeigen explizit im Browser öffnen,
12. ApplicationCases, private Materialien und Dokumente verwalten,
13. künftig explizit reviewbare Bewerbungsentwürfe aus lokalem Profil-/Opportunity-Kontext vorbereiten.

## 5. Core Domain

Die Core Domain ist die persönliche Stellenmarkt-Aufbereitung, Suchstrategie und Entscheidungsunterstützung.

Sie umfasst insbesondere:

- Unterscheidung zwischen Opportunity, Posting, Source und Observation,
- kontrollierte Zusammenführung mehrfach recherchierter Informationen,
- Search-Profile-Semantik und Forschungs-/Evaluationskontext,
- persönliche Eignungsbewertung und erklärbarer Fit,
- Status, Prioritäten, Gruppen/Sammlungen und Ausschlussgründe,
- Aktualität und Verfügbarkeit,
- fachliche und räumliche Vergleiche,
- ApplicationCase- und private Bewerbungszustände.

Candidate Profile-Fakten sind bewusst von Vocation-spezifischer Suchpolitik getrennt. Solange kein zweiter konkreter Consumer eine gemeinsame Person-Profile-Capability rechtfertigt, bleiben sie lokale Vocation-Fakten hinter einer separierbaren Grenze.

## 6. Supporting Capabilities

- Prompt-Erzeugung aus Search Profile, Candidate Profile und aktuellem Bestand/Teilbestand
- Import versionierter JSON-Bundles
- Validierung, Provenienz und Importbericht
- Listen-, Detail-, Vergleichs- und Kartenansichten
- Filter, Sortierung und Suche
- Öffnen externer Originalanzeigen
- ApplicationCase-, ApplicationMaterial- und private ApplicationDocument-Verwaltung
- lokale Dateispeicherung mit Integritätsprüfung
- client-neutrale Published Vocation Capabilities für Wiiii Got This

Die räumliche Fachsicht bleibt Vocation-owned: Work Location, Precision, MapLocationResolution, Map Projection und job-spezifische Informationen/Aktionen gehören zu Vocation. Generisches Place Search/Geocoding und Map Rendering werden über Orientation konsumiert und sind keine Vocation-Domainsemantik.

Dasselbe gilt für künftige Search Areas: Vocation besitzt deren job-spezifische Bedeutung und Radius-/Remote-/Relocation-Politik; generische Ortsauflösung bleibt Orientation-owned.

## 7. Nutzungsablauf

Der aktuell implementierte Basispfad lautet:

1. Der Nutzer pflegt sein Candidate Profile und ein oder mehrere Search Profiles.
2. Er wählt in Vocation einen Recherchemodus.
3. Vocation erzeugt einen vorbereiteten Prompt mit exakt snapshotbarem relevantem Kontext.
4. Der Nutzer prüft und kopiert den Prompt in ein externes Research-Tool.
5. Dort wird die Recherche durchgeführt.
6. Das Tool liefert ein versioniertes JSON-Bundle.
7. Vocation importiert, validiert und übersetzt es kontrolliert.
8. Der Nutzer sichtet Stellenmarkt, Fit, Details, Vergleich und Karte.
9. Bei Bedarf öffnet er die Originalanzeige und prüft/aktualisiert Availability.
10. Spätere Update-Prompts beziehen den vorhandenen Bestand gezielt ein.
11. Für verfolgte Stellen kann der Nutzer einen ApplicationCase mit privaten Materialien/Dokumenten pflegen.

Die manuelle Produktabnahme hat gezeigt, dass die aktuelle UI dieses Modell noch nicht ausreichend klar und effizient präsentiert. Die akzeptierte Post-v0.4-Richtung ist in `17_MANUAL_PRODUCT_ACCEPTANCE.md` dokumentiert.

## 8. Gerätebezogene Nutzung

Desktop/local product:

- Candidate-/Search-Profile-Pflege,
- Prompt-Erzeugung,
- Datei-/Clipboard-Import,
- vollständige Validierungsberichte,
- komplexe Filter und Vergleiche,
- Kartenansicht,
- Originalanzeigen öffnen,
- ApplicationCase-/Dokument-Pflege,
- administrative/fortgeschrittene Pflege.

Cross-device Nutzung über Wiiii Got This kann geeignete explizit veröffentlichte/protected Vocation Capabilities konsumieren. Das überträgt keine Vocation-Fachautorität an WGT oder Conveyance.

## 9. Abgrenzung

Vocation ist nicht verantwortlich für:

- automatisches Absenden von Bewerbungen,
- unbeaufsichtigtes Schreiben/Versenden von Bewerbungen ohne Review,
- Kommunikation mit Unternehmen,
- E-Mail- oder Kalenderverwaltung,
- Lern- und Übungsverwaltung,
- vollständiges automatisches Crawling aller Stellenportale,
- implizite eigene kostenpflichtige LLM-Recherche,
- versteckte Übermittlung privater Profile/Dokumente,
- Verwaltung anderer Services,
- generische Map-/Geocoding-/Routing-Semantik.

Explizit prompt-assistierte, vom Nutzer geprüfte **Bewerbungsentwürfe** sind dagegen geplante Vocation-Produktarbeit (#50) und nicht mit automatischem Bewerbungsversand gleichzusetzen.

## 10. Beziehungen

### External Research Context

Erzeugt Research-/Update-/Availability-Ausgaben nach den jeweils versionierten Verträgen. Vocation übersetzt diese über kontrollierte Grenzen und bleibt autoritativ für lokalen Zustand, Interpretation und persönliche Entscheidungen.

### Wiiii Got This

Kann geeignete Vocation-owned Published/protected Capabilities auf unterschiedlichen Geräten präsentieren. Es liest nie die Vocation-Datenbank und besitzt keine Vocation-Fachlogik.

Vocation veröffentlicht versionierte, client-neutrale Read Projections über einen Vocation-eigenen Publication Adapter. Eine optionale Conveyance-Zustellung transportiert nur opaque geschützte, abgeleitete Artefakte; Conveyance versteht keine Vocation-Domainobjekte.

### Orientation

Ist der systemweit akzeptierte generische Geospatial-/Place-Bounded-Context. Vocation konsumiert Orientation für generisches Place Search/Geocoding und Map Rendering über explizite Adapter-/Host-Grenzen.

Vocation bleibt autoritativ für Work Location, Search Area, Radius-/Arbeitsortpräferenzen, Precision, MapLocationResolution, Opportunity, Company, Availability, External Links und alle daraus abgeleiteten fachlichen Aktionen.

### Future document understanding

PDF-Text-/Layout-/OCR-Extraktion wird nicht allein aus Implementierungsbequemlichkeit als Microservice eingeführt. Zunächst ist sie ein ersetzbarer Port an der Vocation-Grenze. Ein separater generischer Document-Understanding-Service wird erst gerechtfertigt, wenn ein zweiter konkreter Consumer oder eigenständige Runtime-/Security-/Dependency-Anforderungen existieren.

Vocation bleibt in jedem Fall Eigentümer der Interpretation extrahierter Inhalte als Candidate-Profile- oder Application-Semantik.

### Illumination

Eigenständiger Kontext für Lernen. Eine spätere Referenzierung von Lernbedarf ist möglich, aber nicht Bestandteil des aktuellen Vocation-Release-Gates.

## 11. Leitprinzipien

- Herkunft und Zeitpunkt bleiben sichtbar.
- Keine stillen Datenverluste.
- Observation ist nicht Wahrheit.
- Persönliche Entscheidungen und private Zustände werden geschützt.
- Automatische Zusammenführung ist konservativ.
- Externe Links werden nur nach Nutzeraktion geöffnet.
- Prompt-Ausgaben und Importverträge sind versioniert.
- Persönliche Relevanz ist wichtiger als allgemeine Markt-Vollständigkeit.
- Research-Breite und Ergebnisqualität sind getrennt: breite Suche darf wenige gute Treffer ergeben.
- Offizielle aktuelle Originalquellen werden gegenüber alten Aggregator-Hits bevorzugt.
- Vocation bleibt eigenständig und lokal autoritativ.
- Akzeptierte generische System-Capabilities werden nicht unnötig dupliziert.
- Automatisierung muss mehr Zeit sparen als sie kostet und darf keinen versteckten persönlichen Zustand mutieren.
- Technische Testabdeckung ist notwendig, ersetzt aber keine reale Produktabnahme.

## 12. Erfolgskriterien

Vocation ist erfolgreich, wenn:

- relevante Stellen nicht mehr nur in Chats oder Tabs existieren,
- persönliche Profil- und Suchdaten nicht für jeden Run neu eingegeben werden müssen,
- unterschiedliche Search Profiles reproduzierbar ausprobiert werden können,
- Rechercheläufe einheitliche und aktuelle Evidenz mit Quellen liefern,
- verschiedene Suchstrategien/Grinds Marktabdeckung gezielt erhöhen können,
- Updates gezielt statt vollständig neu recherchiert werden können,
- Herkunft, Aktualität und aktiver Bewerbungsweg nachvollziehbar bleiben,
- Dubletten und historische Änderungen kontrolliert behandelt werden,
- Fit und fehlende Evidenz verständlich erklärt werden,
- Karten-/Vergleichsansichten denselben gefilterten Stellenbestand repräsentieren,
- der Nutzer aus einer Opportunity in einen nachvollziehbaren Bewerbungsprozess wechseln kann,
- private CV-/Nachweis-Dokumente wiederverwendbar bleiben,
- der Nutzer den Bestand ohne Chat-Rekonstruktion versteht,
- reale manuelle Produktabnahme die technische Acceptance bestätigt.

## 13. Post-v0.4 Produktfragen und aktuelles Release-Gate

Die stabile v0.4.0-Baseline bleibt abgeschlossen. Die erste manuelle Produktabnahme des post-v0.4-`dev`-Stands hat jedoch neue Blocker identifiziert.

Aktuelle fokussierte Produktarbeit:

- #45 UI-/Informationsarchitektur-Redesign;
- #46 persistentes persönliches Profil und wiederverwendbare CV-/Nachweis-Dokumente;
- #47 strukturierter Search-Profile-Editor, Search Areas und Radien;
- #48 pflegbare Rollen-/Technologie-/Branchenkataloge;
- #49 explizite Research Strategies, Company-first Coverage und Freshness-Verifikation;
- #50 Bewerbungsworkspace und reviewbare prompt-assistierte Bewerbungsentwürfe;
- #52 robuster/diagnostizierbarer Windows-Dev-Launcher.

Weitere bewusste spätere Fragen bleiben unter anderem:

- zukünftige manuelle Auflösung bestätigter Duplicate Cases und mögliche Merge-Regeln,
- private Document-Folgesemantik wie Delete/Retention, Rich Editing/Rendering/Export und Verschlüsselung,
- konkrete private Cross-device-Transport-/Authentisierungsausgestaltung,
- Cross-device Write-Semantik,
- weitere Published Contracts nur bei einem konkreten Consumer-Szenario.

Die finalen Felder von Research Bundle 1.0, Published Opportunity Overview 1.0 und Published Map Projection 1.0 werden durch diese Produktarbeit nicht still erweitert.

Die detaillierten manuellen Acceptance-Funde und die Trennung zwischen implementiertem und geplantem Stand stehen in `17_MANUAL_PRODUCT_ACCEPTANCE.md`.
