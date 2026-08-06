# Vocation – Domain Vision

**Status:** Draft 0.2  
**Purpose:** Fachliche Leitlinie für die Entwicklung von Vocation

## 1. Produktvision

Vocation ist eine eigenständig nutzbare Anwendung zur strukturierten Sichtung, Verwaltung, Bewertung und räumlichen Darstellung von Stellenangeboten.

Die eigentliche Stellenrecherche findet außerhalb von Vocation statt, zunächst insbesondere mithilfe von ChatGPT. Vocation unterstützt diesen Ablauf durch vorbereitete, versionierte Prompt-Vorlagen für:

- initiale Recherche,
- Aktualisierung eines bestehenden Bestands,
- Aktualisierung ausgewählter Unternehmen oder Stellen,
- Nachrecherche fehlender oder widersprüchlicher Felder,
- Erzeugung eines vollständig schema-konformen Research Bundle.

Vocation übernimmt die erzeugten JSON-Daten, validiert sie und stellt sie dauerhaft übersichtlich bereit.

## 2. Fachliches Problem

Ein persönlicher Stellenmarkt besteht nicht nur aus Links. Für belastbare Entscheidungen müssen gemeinsam betrachtet werden:

- konkrete berufliche Möglichkeit,
- veröffentlichte Anzeigen und Quellen,
- Unternehmen, Team und Arbeitsort,
- Technologien und Aufgaben,
- Junior-Eignung und Erfahrungsanforderungen,
- Veröffentlichungs- und Recherchezeitpunkt,
- Verfügbarkeit,
- externe und persönliche Bewertung,
- Risiken, Ausschlüsse und Prioritäten,
- Bewerbungswellen oder andere Gruppen,
- räumliche Verteilung,
- Originalanzeige.

Chats können diese Informationen analysieren, aber schlecht dauerhaft pflegen. Vocation überführt sie in einen strukturierten, nachvollziehbaren Bestand.

## 3. Zielnutzer

Vocation wird zunächst für einen einzelnen Nutzer entwickelt. Es ist kein allgemeines Recruiting-Portal, kein ATS und kein Bewerbungsversand-System.

## 4. Zentrale fachliche Fähigkeit

> Extern recherchierte Stelleninformationen kontrolliert in einen nachvollziehbaren, vergleichbaren und dauerhaft nutzbaren persönlichen Stellenbestand überführen.

Dazu gehören:

1. standardisierte Rechercheprompts erzeugen,
2. versionierte Research Bundles importieren,
3. Format und fachliche Konsistenz prüfen,
4. Job Opportunities, Job Postings, Sources und Observations zuordnen,
5. aktuelle und historische Informationen unterscheiden,
6. Bewertungen und persönliche Entscheidungen trennen,
7. Bestände filtern, gruppieren und vergleichen,
8. räumliche Zusammenhänge sichtbar machen,
9. Originalanzeigen aus Vocation heraus explizit im Browser öffnen.

## 5. Core Domain

Die Core Domain ist die persönliche Stellenmarkt-Aufbereitung und Entscheidungsunterstützung.

Sie umfasst insbesondere:

- Zusammenführen mehrfach recherchierter Informationen,
- Unterscheidung zwischen Opportunity, Posting, Source und Observation,
- persönliche Eignungsbewertung,
- Status, Prioritäten, Gruppen und Ausschlussgründe,
- Aktualität und Verfügbarkeit,
- fachliche und räumliche Vergleiche.

## 6. Supporting Capabilities

- Prompt-Erzeugung aus aktuellem Bestand oder Teilbestand
- Import versionierter JSON-Dateien
- Validierung und Importbericht
- Tabellen-, Detail-, Vergleichs- und Kartenansichten
- Filter, Sortierung und Suche
- Öffnen externer Originalanzeigen
- Read Models für spätere mobile Clients

## 7. Nutzungsaublauf

1. Der Nutzer wählt in Vocation einen Recherchemodus.
2. Vocation erzeugt einen vorbereiteten Prompt mit relevantem Kontext.
3. Der Nutzer kopiert den Prompt in ChatGPT.
4. Die Recherche wird dort durchgeführt.
5. ChatGPT liefert ein versioniertes JSON Research Bundle.
6. Der Nutzer speichert oder kopiert das Bundle.
7. Vocation importiert, validiert und übersetzt es.
8. Der Nutzer sichtet Liste, Details, Vergleich und Karte.
9. Bei Bedarf öffnet er die Originalanzeige im Browser.
10. Spätere Update-Prompts beziehen den vorhandenen Bestand gezielt ein.

## 8. Gerätebezogene Nutzung

Desktop:

- Prompt-Erzeugung
- Datei-/Clipboard-Import
- vollständige Validierungsberichte
- komplexe Filter und Vergleiche
- Kartenansicht
- Originalanzeigen öffnen
- fachliche Pflege

Spätere mobile Nutzung:

- Stellenliste
- Detailansicht
- Kartenansicht
- Filter und Vergleich
- Datenstand und Freshness
- externe Originalanzeige im Browser öffnen

Nicht zwingend mobil:

- Prompt-Generierung mit umfangreichem Bestandskontext
- JSON-Import
- Fehlerkorrektur
- administrative Pflege

## 9. Abgrenzung

Vocation ist nicht verantwortlich für:

- automatisches Versenden von Bewerbungen,
- automatisches Schreiben von Bewerbungen,
- Kommunikation mit Unternehmen,
- E-Mail- oder Kalenderverwaltung,
- Lern- und Übungsverwaltung,
- vollständiges Crawling aller Stellenportale,
- eigene LLM-Recherche,
- kostenpflichtige LLM-API-Aufrufe,
- Verwaltung anderer Services.

## 10. Beziehungen

### External Research Context

Erzeugt Research Bundles. Vocation übersetzt diese über eine Anticorruption Layer.

### Wiiii Got This

Kann Vocation später geräte- und plattformabhängig integrieren. Vocation bleibt eigenständig.

### Illumination

Eigenständiger Kontext für Lernen. Eine spätere Referenzierung von Lernbedarf ist möglich, aber nicht Teil von Vocation Version 1.

## 11. Leitprinzipien

- Herkunft und Zeitpunkt bleiben sichtbar.
- Keine stillen Datenverluste.
- Observation ist nicht Wahrheit.
- Persönliche Entscheidungen werden geschützt.
- Automatische Zusammenführung ist konservativ.
- Externe Links werden nur nach Nutzeraktion geöffnet.
- Prompt-Ausgaben und Importverträge sind versioniert.
- Persönliche Relevanz ist wichtiger als allgemeine Markt-Vollständigkeit.
- Vocation bleibt eigenständig.
- Automatisierung muss mehr Zeit sparen als sie kostet.

## 12. Erfolgskriterien

Vocation ist erfolgreich, wenn:

- relevante Stellen nicht mehr nur in Chats oder Tabs existieren,
- Rechercheläufe einheitliche Daten liefern,
- Updates gezielt statt vollständig neu recherchiert werden können,
- Herkunft und Aktualität nachvollziehbar bleiben,
- Dubletten und historische Änderungen kontrolliert behandelt werden,
- Stellen auf korrekten oder gekennzeichnet approximierten Positionen erscheinen,
- ein Karten-Pin direkt zur Vocation-Detailansicht und von dort zur Originalanzeige führen kann,
- der Nutzer den Bestand ohne Chat-Rekonstruktion versteht,
- neue Importe den Bestand kontrolliert ergänzen.

## 13. Offene Fachfragen

- genaue Identitätsregeln für Opportunities und Postings,
- automatische versus manuelle Zusammenführung,
- Umfang persönlicher Änderungen,
- Bewerbungsstatus innerhalb oder außerhalb Vocation,
- Form mobiler Read Models,
- Zeitpunkt für einen zentralen Kartendienst.
