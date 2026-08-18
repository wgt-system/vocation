# Vocation – Usage Scenarios

**Status:** v0.4.0 scenarios implemented where marked by the stable baseline; post-v0.4 profile/fit/research capabilities implemented on `dev`; S26–S31 describe accepted product direction that is not yet fully implemented.

## Zweck

Die Szenarien konkretisieren die Domain Vision und bilden die Grundlage für Ubiquitous Language, Domain Model, Application Use Cases und Acceptance Tests.

Interne Domain-Begriffe und user-facing UI-Bezeichnungen sind bewusst getrennt. Ein `OpportunityGroup` oder eine `ApplicationWave` kann intern stabil bleiben, auch wenn die Produktoberfläche später verständlichere deutsche Begriffe verwendet.

## S01 – Erster Research-Bundle-Import

Der Nutzer lässt mit einem von Vocation erzeugten Initial-Prompt eine erste Recherche durchführen. Der Prompt verwendet ein persistentes Search Profile und optional den aktuellen Candidate-Profile-Snapshot. Das Ergebnis liegt als versioniertes JSON vor. Vocation validiert das Bundle, verknüpft es bei normalem Inline-Flow mit dem Prompt Context, importiert gültige Inhalte und zeigt anschließend den persönlichen Stellenmarkt.

## S02 – Update des Gesamtbestands

Vocation erzeugt einen Update-Prompt mit scope-bezogenem Kontext und offenen Unsicherheiten. Der Import ergänzt den Bestand, ohne persönliche Decisions, Tracking Status, Notizen oder Application-State zu überschreiben.

## S03 – Teilupdate eines Unternehmens

Der Nutzer wählt eine Company. Vocation erzeugt einen Prompt, der nur bekannte Opportunities, Postings und offene Fragen dieses Unternehmens enthält. Das zurückgelieferte Bundle darf nur den definierten Scope betreffen.

## S04 – Nachrecherche fehlender Felder

Bei einzelnen Opportunities fehlen Arbeitsort, Gehalt, Junior-Eignung oder andere für Search Profile/Fit wichtige Evidenz. Vocation erstellt einen Prompt mit genau diesen Lücken und den relevanten Quellen. Das Ergebnis wird als zusätzliche externe Evidenz importiert.

## S05 – Erneuter Fund derselben Stelle

Eine bekannte Stelle wird erneut gefunden. Vocation erkennt sichere Posting-Identität über die akzeptierten deterministischen Regeln und ergänzt Evidenz, statt unkontrolliert ein zweites Posting anzulegen.

## S06 – Mögliche Dublette

Zwei Subjects sind ähnlich, aber nicht sicher identisch. Vocation erzeugt einen Duplicate Case. Eine automatische irreversible Zusammenführung findet nicht statt.

## S07 – Nicht mehr erreichbare Anzeige

Ein Availability Check meldet das Ergebnis für ein bekanntes Posting. Vocation speichert die Availability Observation append-only, behält historische Inhalte und unterscheidet Posting-Unavailability von Opportunity-Closure. Temporäre oder unzuverlässige Ergebnisse führen zu `uncertain`, nicht automatisch zu `unavailable`.

## S08 – Widersprüchliche Quellen

Zwei Quellen nennen unterschiedliche Standorte oder Arbeitsmodelle. Vocation zeigt Widerspruch, Herkunft und Zeitpunkte. Ein bevorzugter Wert darf nur anhand dokumentierter Regeln oder persönlicher Bestätigung entstehen.

## S09 – Persönlicher Ausschluss

Der Nutzer schließt eine Opportunity mit Grund aus. Ein späterer Import darf diese Decision nicht aufheben. Eine wesentlich veränderte oder neu veröffentlichte Opportunity kann separat bewertet werden.

## S10 – Opportunity Group oder Application Wave

Der Nutzer erstellt intern eine `OpportunityGroup` vom Typ `general` oder `application_wave`, fügt Opportunities in expliziter Reihenfolge hinzu, entfernt oder ordnet sie neu. Eine Application Wave ist kein separates Aggregate. Gruppen verändern weder Identität noch Historie der Opportunities und lösen keine Bewerbungs- oder Statusautomatik aus.

Die manuelle Produktabnahme hat die literal user-facing Darstellung `Groups/Waves` nicht akzeptiert. Eine spätere Oberfläche darf dieselbe Domänensemantik als verständlichere Sammlung/Bewerbungsphase präsentieren.

## S11 – Vergleich

Der Nutzer wählt 2 bis 4 bestehende Opportunities in expliziter Reihenfolge und öffnet den Vergleich. Die read-only Ansicht zeigt Research-/Assessment-Dimensionen mit expliziten Missing-States und ohne versteckten Winner Selector. Erklärbarer Search-Profile-Fit kann als separate nachvollziehbare Vocation-Sicht verwendet werden; der Vergleich selbst bleibt keine zweite Scoring-Engine.

## S12 – Kartenansicht

Die Karte zeigt die aktuell gefilterte Menge an Opportunities an aufgelösten Work Locations. Eine explizite Nutzeraktion kann für eine WorkLocation eine manuelle oder Orientation-basierte MapLocationResolution anlegen oder ersetzen. Geocoding erhöht die Research-Precision nicht.

## S13 – Originalanzeige aus Karten-/Detailansicht öffnen

Der Nutzer löst explizit die Browser-Aktion für einen gültigen ExternalLink aus. Vocation öffnet nie ohne Nutzeraktion und bevorzugt Links deterministisch nach der implementierten External-Link-Policy.

## S14 – Mehrere Postings für eine Opportunity

Eine Opportunity besitzt mehrere Posting-Link-Kandidaten. Vocation zeigt Quellen und Availability. Der Nutzer wählt einen Link oder verwendet den deterministisch bevorzugten Link.

## S15 – Ungültige externe URL

Eine Source Reference ist syntaktisch ungültig oder verwendet ein nicht erlaubtes Schema. Vocation öffnet sie nicht und zeigt einen verständlichen Fehler.

## S16 – Fehlerhaftes Bundle

Das JSON ist syntaktisch korrekt, aber fachlich unvollständig oder scope-widrig. Vocation unterscheidet Blocker, Entry-Fehler und Warnungen und schützt den bestehenden Datenbestand vor partieller unkontrollierter Mutation.

## S17 – Wiederholter Import derselben Datei

Ein identischer Bundle-Fingerprint wurde bereits angewendet. Vocation verhindert eine unkontrollierte Doppelanwendung und zeigt den früheren Import an.

## S18 – WGT Published Read Projection

WGT liest eine client-neutrale Published Vocation Projection. Import und fachliche Autorität bleiben Vocation-owned. Ein Consumer liest weder Vocation-Datenbank noch Domainklassen direkt.

## S19 – Publication Snapshot Age

Eine Publication Snapshot ist älter als der lokale Bestand. Das Veröffentlichungsalter wird sichtbar; es bedeutet nicht, dass ein Job Posting stale oder unavailable ist.

## S20 – Local-only Operation

Wenn keine Remote-Publikation konfiguriert ist, bleiben lokale Prompting-, Import-, Pflege-, Profil-, Bewerbungs- und Read-Workflows vollständig nutzbar.

## S21 – Historische Opportunity wird erneut relevant

Eine früher ausgeschlossene oder archivierte Position erscheint mit veränderten Anforderungen. Historische Decisions bleiben sichtbar und werden nicht blind übertragen.

## S22 – ApplicationCase verwalten

Der Nutzer erstellt für eine Opportunity explizit einen `ApplicationCase` und führt ihn durch `draft`, `ready`, `submitted`, `interviewing` und `offer` oder in einen terminalen Zustand `accepted`, `rejected` oder `withdrawn`. ApplicationCase-Lifecycle ist unabhängig vom Opportunity Tracking Status; jede Änderung bleibt als Historie sichtbar.

## S23 – Privates ApplicationDocument anhängen

Eine ApplicationMaterial-Revision kann explizit null oder ein privates `ApplicationDocument` besitzen. Das Dokument ist unveränderlich an genau diese Revision gebunden; Ersatz erfolgt nur über eine neue Material-Revision. Vocation bewahrt Integritätsmetadaten und veröffentlicht weder Payload noch private Dokument-Metadaten.

## S24 – Privates ApplicationDocument explizit öffnen

Der Nutzer wählt für eine ApplicationMaterial-Revision die explizite Aktion `Öffnen`. Vocation löst genau das angezeigte `ApplicationDocument` auf, validiert Byte Size und SHA-256 gegen die persistierten Metadaten und gibt erst danach die unveränderlichen privaten Bytes mit dem persistierten Media Type zurück.

## S25 – Mögliche Dublette manuell entscheiden

Der Nutzer prüft einen bestehenden Opportunity- oder Posting-DuplicateCase anhand der Subjects, Evidence und Source References. Er entscheidet explizit `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` oder `keep_unresolved` mit Grund. Jede Entscheidung wird append-only historisiert; `confirmed_duplicate` führt keinen Merge aus.

## S26 – Persistentes persönliches Profil und wiederverwendbare Dokumente (geplant, #46)

Der Nutzer pflegt persönliche Bewerbungs-/Karrieredaten einmal strukturiert und kann CV, Abschlusszeugnisse, Arbeitszeugnisse oder andere Nachweise lokal ablegen. Mehrere Search Profiles und ApplicationCases können diese Fakten/Dokumente referenzieren, ohne sie zu duplizieren oder erneut hochzuladen.

Dokumente werden nicht automatisch an externe Research-Tools gesendet.

## S27 – Dokument schlägt Profile-Fakten vor (später, #46)

Der Nutzer startet explizit eine Extraktion eines CVs oder Zeugnisses. Ein ersetzbarer Document-Extraction-Adapter liefert Text/strukturierte Vorschläge mit Provenienz. Vocation zeigt Vorschläge zur Prüfung; erst eine explizite Nutzeraktion erzeugt neue Candidate-Profile-Fakten/Revisionen. OCR-/Parser-Ausgabe überschreibt nie still den persönlichen Zustand.

## S28 – Strukturiertes Search Profile mit mehreren Search Areas (geplant, #47/#48)

Der Nutzer wählt Rollen, Seniority, Beschäftigungsarten, Technologien und Branchen über durchsuchbare kontrollierte Werte und kann bei Bedarf neue Custom Terms hinzufügen. Für Hamburg, Berlin oder andere Orte wählt er generische Orte über Orientation Place Search und ergänzt optional einen Radius. Remote/Relocation sind eigene Suchsemantiken und keine Fake-Orte.

## S29 – Company-first Research Grind (geplant, #49)

Der Nutzer wählt ein Search Profile und startet einen Company-first Grind. Vocation generiert einen Prompt für einen definierten Unternehmens-/Coverage-Scope. Das externe Research-Tool prüft bevorzugt offizielle Karriereseiten umfassend, sucht nicht nur nach Titeln mit `Junior`, verifiziert konkrete aktive Bewerbungswege und liefert nur ausreichend passende, evidenzbasierte Opportunities zurück.

Vocation merkt sich, welche Companies geprüft wurden und ob relevante aktuelle Rollen gefunden wurden, auch wenn ein Run null importierbare Opportunities ergibt.

## S30 – Freshness-Recheck einer älteren Stelle (geplant/auf bestehender Availability-Semantik, #49)

Eine vor Wochen gefundene Stelle ist fachlich interessant, aber ihr Alter ist ein Warnsignal. Der Nutzer startet einen gezielten Freshness-/Availability-Check auf dem Originalposting. Eine explizit nicht mehr verfügbare Stelle bleibt historisch erhalten, wird aber nicht weiter als aktuell actionable präsentiert. Alter allein bedeutet nicht `unavailable`.

## S31 – Bewerbungsentwurf aus Opportunity und Profil erzeugen (geplant, #50)

Der Nutzer öffnet eine Opportunity/ApplicationCase, wählt einen exakten Candidate-Profile-Snapshot und bewusst ausgewählte private Dokument-/Faktengrundlagen. Vocation erzeugt einen transparenten Prompt für z. B. Anschreiben oder Bewerbungsnachricht. Das externe Ergebnis ist ein privater Entwurf, der erst nach Nutzerprüfung als neue Material-Revision gespeichert wird. Es gibt keinen automatischen Versand.

## Übergreifende Regeln

1. Herkunft und Zeitpunkt jeder externen Information bleiben erhalten.
2. Prompt- und Importverträge sind versioniert.
3. Teilupdates dürfen ihren Scope nicht still überschreiten.
4. Persönliche Decisions, Notizen, Profile und Application-State werden nie durch Research-Imports überschrieben.
5. Externe Links werden nur nach Nutzeraktion geöffnet.
6. Die Karte besitzt keine eigene fachliche Datenhoheit.
7. Published/consumer-spezifische Sichten übertragen keine Vocation-Fachautorität.
8. Research, Availability und Groups/Waves erzeugen oder verändern keine ApplicationCases.
9. Research-Imports erzeugen mögliche Duplicate Cases, aber niemals persönliche Duplicate Decisions oder Identitäts-Merges.
10. Externe Research-/Extraction-/Generation-Ausgaben sind Vorschläge/Evidenz und mutieren private Vocation-Fakten nur über explizite akzeptierte Use Cases.
11. Interne Domänenbegriffe müssen nicht literal als Produktnavigation erscheinen.
12. Ein grüner automatisierter Acceptance-Test ersetzt keine reale manuelle Produktabnahme.
