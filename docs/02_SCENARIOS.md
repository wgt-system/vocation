# Vocation – Usage Scenarios

**Status:** Draft 0.2

## Zweck

Die Szenarien konkretisieren die Domain Vision und bilden die Grundlage für Ubiquitous Language, Domain Model, Application Use Cases und Acceptance Tests.

## S01 – Erster Research-Bundle-Import

Der Nutzer lässt mit einem von Vocation erzeugten Initial-Prompt eine erste Recherche durchführen. Das Ergebnis liegt als versioniertes JSON vor. Vocation validiert das Bundle, importiert gültige Inhalte, weist Fehler nachvollziehbar aus und zeigt anschließend Liste, Details und Karte.

## S02 – Update des Gesamtbestands

Vocation erzeugt einen Update-Prompt mit scope-bezogenem Kontext und offenen Unsicherheiten. Im v0.3 enthält Full Update keine Availability/Freshness. Der Import ergänzt den Bestand, ohne persönliche Decisions zu überschreiben.

## S03 – Teilupdate eines Unternehmens

Der Nutzer wählt eine Company. Vocation erzeugt einen Prompt, der nur bekannte Opportunities, Postings und offene Fragen dieses Unternehmens enthält. Das zurückgelieferte Bundle darf nur den definierten Scope betreffen.

## S04 – Nachrecherche fehlender Felder

Bei einzelnen Opportunities fehlen Arbeitsort, Gehalt oder Junior-Eignung. Vocation erstellt einen Prompt mit genau diesen Lücken und den zugehörigen Quellen. Das Ergebnis wird als zusätzliche Observations importiert.

## S05 – Erneuter Fund derselben Stelle

Eine bekannte Stelle wird erneut gefunden. Vocation erkennt gleiche externe IDs oder einen sicheren Match und ergänzt Observations, statt eine zweite Opportunity anzulegen.

## S06 – Mögliche Dublette

Zwei Postings sind ähnlich, aber nicht sicher identisch. Vocation erzeugt einen Duplicate Case. Eine automatische irreversible Zusammenführung findet nicht statt.

## S07 – Nicht mehr erreichbare Anzeige

Ein Availability Check meldet das Ergebnis für ein bekanntes Posting. Vocation speichert die Availability Observation append-only, behält historische Inhalte und unterscheidet Posting-Unavailability von Opportunity-Closure. Temporäre oder unzuverlässige Ergebnisse führen zu `uncertain`, nicht definitiv zu `unavailable`.

## S08 – Widersprüchliche Quellen

Zwei Quellen nennen unterschiedliche Standorte oder Arbeitsmodelle. Vocation zeigt Widerspruch, Herkunft und Zeitpunkte. Ein bevorzugter Wert darf nur anhand dokumentierter Regeln oder persönlicher Bestätigung entstehen.

## S09 – Persönlicher Ausschluss

Der Nutzer schließt eine Opportunity mit Grund aus. Ein späterer Import darf diese Decision nicht aufheben. Eine wesentlich veränderte oder neu veröffentlichte Opportunity kann separat bewertet werden.

## S10 – Opportunity Group oder Application Wave

Der Nutzer erstellt eine `OpportunityGroup` vom Typ `general` oder `application_wave`, fügt Opportunities in expliziter Reihenfolge hinzu, entfernt oder ordnet sie neu. Eine Application Wave ist dabei keine eigene Aggregate-Klasse. Gruppen verändern weder Identität noch Historie der Opportunities und lösen keine Bewerbungs- oder Statusautomatik aus.

## S11 – Vergleich

Der Nutzer wählt 2 bis 4 bestehende Opportunities in expliziter Reihenfolge und öffnet `Vergleichen`. Die implementierte read-only Ansicht zeigt Technologien, Aufgaben, Seniorität, Erfahrung, Arbeitsmodell, Gehalt, WorkLocations, Availability-/Evidence-Freshness, Assessments und Groups/Waves spaltenweise. Fehlende Werte bleiben explizit fehlend; mehrere Evidenzwerte bleiben sichtbar und werden nicht automatisch als widersprüchlich, bewertet oder gerankt. Risk-Vergleich bleibt bis zu einer konkreten Risk-Read-Quelle später.

## S12 – Kartenansicht

Die Karte zeigt die aktuell gefilterte Menge an Opportunities an aufgelösten Work Locations. Eine explizite Nutzeraktion kann für eine WorkLocation eine manuelle oder geocoderbasierte MapLocationResolution anlegen oder ersetzen. Precision und approximierte Positionen bleiben die der WorkLocation. Ein Pin öffnet ausschließlich eine Vocation-Vorschau oder Detailansicht; externe Navigation gehört zu Slice 12.

## S13 – Originalanzeige aus Karten-Pin öffnen

Der Nutzer klickt auf einen Company- oder Opportunity-Pin. Die Vorschau zeigt gültige ExternalLink-Kandidaten und Posting Availability. Durch eine explizite Aktion öffnet Vocation die ausgewählte Originalanzeige im Standardbrowser. Vocation darf den Browser nicht ohne Nutzeraktion öffnen.

## S14 – Mehrere Postings an einem Pin

Eine Opportunity besitzt mehrere Posting-Link-Kandidaten. Der Pin zeigt Quellen und Availability. Der Nutzer wählt die gewünschte Originalanzeige oder verwendet den deterministisch bevorzugten Link.

## S15 – Ungültige externe URL

Eine Source Reference ist syntaktisch ungültig oder verwendet ein nicht erlaubtes Schema. Vocation öffnet sie nicht und zeigt einen verständlichen Fehler.

## S16 – Fehlerhaftes Bundle

Das JSON ist syntaktisch korrekt, aber fachlich unvollständig. Vocation unterscheidet Bundle-Blocker, Entry-Fehler und Warnungen und schützt den bestehenden Datenbestand.

## S17 – Wiederholter Import derselben Datei

Ein identischer Bundle-Fingerprint wurde bereits angewendet. Vocation verhindert eine unkontrollierte Doppelanwendung und zeigt den früheren Import an.

## S18 – WGT Published Read Projection

WGT liest eine client-neutrale Published Opportunity Overview. Import und Prompt-Erzeugung bleiben Vocation-Desktop-Aufgaben. Die letzte veröffentlichte Projection bleibt auf dem iPhone nutzbar, wenn der Windows-PC ausgeschaltet ist.

## S19 – Publication Snapshot Age

Eine Publication Snapshot ist älter als der lokale Bestand. Das Veröffentlichungsalter wird sichtbar; es bedeutet nicht, dass ein Job Posting stale oder unavailable ist.

## S20 – Local-only Operation

Wenn keine Remote-Publikation konfiguriert ist, bleiben lokale Prompting-, Import-, Pflege- und Read-Workflows vollständig nutzbar.

## S21 – Historische Opportunity wird erneut relevant

Eine früher ausgeschlossene oder archivierte Position erscheint mit veränderten Anforderungen. Historische Decisions bleiben sichtbar, werden aber nicht blind übertragen.

## S23 – Privates ApplicationDocument anhängen

Eine ApplicationMaterial-Revision kann explizit null oder ein privates `ApplicationDocument` besitzen. Das Dokument ist unveränderlich an genau diese Revision gebunden; Ersatz erfolgt nur über eine neue Material-Revision. Vocation bewahrt Integritätsmetadaten, veröffentlicht aber weder Payload noch Dokument-Metadaten.

## S22 – ApplicationCase verwalten

Der Nutzer erstellt für eine Opportunity explizit einen ApplicationCase und führt ihn durch `draft`, `ready`, `submitted`, `interviewing` und `offer` oder in einen terminalen Zustand `accepted`, `rejected` oder `withdrawn`. ApplicationCase-Lifecycle ist unabhängig vom Opportunity Tracking Status; jede Änderung bleibt als Historie sichtbar. Private ApplicationMaterial-Metadaten werden revisionsbezogen verwaltet, ohne Inhalte in Research, Publikationen oder öffentliche Fixtures zu übernehmen.

## Übergreifende Regeln

1. Herkunft und Zeitpunkt jeder externen Information bleiben erhalten.
2. Prompt- und Importverträge sind versioniert.
3. Teilupdates dürfen ihren Scope nicht still überschreiten.
4. Persönliche Decisions werden nie durch Imports überschrieben.
5. Externe Links werden nur nach Nutzeraktion geöffnet.
6. Die Karte besitzt keine eigene fachliche Datenhoheit.
7. WGT-Clients benötigen nicht denselben Funktionsumfang wie die Vocation-Desktop-Anwendung.
8. Research, Availability und Groups/Waves erzeugen oder verändern keine ApplicationCases.
