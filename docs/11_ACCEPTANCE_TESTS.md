# Vocation – Acceptance Tests

**Status:** Draft 0.1

## AT-01 Initialer Import

Gegeben ein gültiges Initial Research Bundle  
Wenn der Nutzer es importiert  
Dann werden Opportunities, Postings, Sources, Observations und External Assessments angelegt  
Und ein erfolgreicher Import Record wird gespeichert.

## AT-02 Identischer Import

Gegeben ein bereits angewendetes Bundle  
Wenn dasselbe Bundle erneut importiert wird  
Dann entstehen keine doppelten Domänenobjekte  
Und der bestehende Import wird referenziert.

## AT-03 Persönliche Decision geschützt

Gegeben eine ausgeschlossene Opportunity  
Und ein Update Bundle mit einer gegenteiligen Empfehlung  
Wenn das Bundle importiert wird  
Dann bleibt die Exclusion bestehen  
Und die Empfehlung wird nur als External Assessment gespeichert.

## AT-04 Sichere Posting-Zuordnung

Gegeben ein bekanntes Posting mit stabiler Source ID  
Wenn ein Update dieselbe externe Posting-ID liefert  
Dann wird keine zweite Posting Entity erzeugt.

## AT-05 Unsichere Dublette

Gegeben zwei ähnliche Postings ohne sicheren Identifier  
Wenn sie importiert werden  
Dann wird kein automatischer Merge durchgeführt  
Und ein Duplicate Case wird angelegt.

## AT-06 Availability

Gegeben eine bisher erreichbare Anzeige  
Wenn ein Update `explicitly_unavailable` meldet  
Dann bleibt das Posting historisch erhalten  
Und die aktuelle Availability wird nachvollziehbar geändert.

## AT-07 Temporärer Fehler

Wenn eine Source nur `temporarily_unreachable` ist  
Dann wird die Opportunity nicht als definitiv geschlossen markiert.

## AT-08 Prompt Initial Research

Wenn der Nutzer einen Initial Research Prompt erzeugt  
Dann enthält der Prompt die gewünschte Bundle Version, das reine JSON-Ausgabeformat und keine nicht benötigten Bestandsdaten.

## AT-09 Prompt Full Update

Wenn ein Full Update Prompt erzeugt wird  
Dann enthält er bekannte IDs, Freshness, offene Unsicherheiten und den erlaubten Änderungsumfang.

## AT-10 Prompt Teilupdate

Wenn ein Company Update Prompt erzeugt wird  
Dann enthält er nur den gewählten Company-Scope  
Und kennzeichnet außerhalb liegende Informationen als nicht zu übernehmen.

## AT-11 Gap Filling

Wenn für eine Opportunity fehlende Felder ausgewählt werden  
Dann fordert der Prompt nur diese Felder und relevante Quellen an.

## AT-12 Import falsche Version

Wenn ein Bundle eine unbekannte Version besitzt  
Dann wird es ohne Domänenänderungen abgelehnt.

## AT-13 Ungültige URL

Wenn ein Posting eine `javascript:`-URL enthält  
Dann wird der Import abgelehnt oder der Link als ungültig markiert  
Und er kann nicht geöffnet werden.

## AT-14 Karte zeigt Precision

Wenn eine Location nur `approximate` ist  
Dann ist dies in der Karte erkennbar.

## AT-15 Pin öffnet Detail

Wenn der Nutzer einen Pin anklickt  
Dann wird eine Vocation-Vorschau oder Detailansicht geöffnet  
Und noch keine externe URL.

## AT-16 Originalanzeige öffnen

Wenn der Nutzer in der Vorschau eine Source auswählt  
Dann wird die validierte URL im Standardbrowser geöffnet.

## AT-17 Mehrere Posting-Links

Wenn mehrere Postings verfügbar sind  
Dann kann der Nutzer die Quelle auswählen  
Oder Vocation markiert einen nachvollziehbar bevorzugten Link.

## AT-18 Kein Link

Wenn kein gültiger Link existiert  
Dann zeigt Vocation einen verständlichen Zustand  
Und startet keinen Browser.

## AT-19 Filterkonsistenz

Wenn ein Filter in der Stellenliste gesetzt ist  
Dann zeigt die Karte dieselbe Opportunity-Menge.

## AT-20 Historie

Wenn ein neuer Import einen Wert verändert  
Dann bleibt die ältere Observation erhalten.

## AT-21 Read-only Mobile

Wenn ein mobiler Client den Read Contract verwendet  
Dann kann er keine Import- oder Decision-Commands ausführen.

## AT-22 Snapshot Freshness

Wenn ein mobiler Snapshot veraltet ist  
Dann zeigt das Read Model den Snapshot-Zeitpunkt und Stale Status.

## AT-23 Exclusion mit Grund

Wenn eine Opportunity ausgeschlossen wird  
Dann ist mindestens ein Exclusion Reason erforderlich.

## AT-24 Restore

Wenn eine Exclusion aufgehoben wird  
Dann bleibt die frühere Decision in der Historie sichtbar.

## AT-25 Keine automatische API-Nutzung

Vocation erzeugt Prompts und importiert JSON  
Aber ruft keine kostenpflichtige LLM-API auf.

## AT-26 Assessment Criteria gehören Vocation

Gegeben ein aktiver Vocation Criteria Catalog
Wenn ein Initial Research Prompt erzeugt wird
Dann enthält er jedes aktive und kein inaktives Criterion mit Value Type und erlaubter Skala oder Werten.

## AT-27 Unbekanntes Criterion

Wenn ein Bundle ein Vocation unbekanntes Criterion referenziert
Dann wird der gesamte Import ohne fachliche Änderungen abgelehnt.

## AT-28 Geschlossene Bundle-Objekte

Wenn ein verschachteltes Bundle-Objekt eine unbekannte oder geschützte Property enthält
Dann wird der gesamte Import ohne fachliche Änderungen abgelehnt.

## AT-29 Atomarer Initial Import

Gegeben ein Bundle mit mindestens einem blockierenden Fehler
Wenn der Nutzer es importiert
Dann werden keine Companies, Opportunities, Postings, Observations oder Assessments daraus gespeichert
Und der Import Report enthält alle erkannten Blocker.

## AT-30 Kanonischer Fingerprint

Gegeben zwei semantisch identische Bundles mit unterschiedlicher Object-Key-Reihenfolge und unterschiedlichem Whitespace
Wenn beide importiert werden
Dann wird nur der erste Import angewendet und der zweite als identisch erkannt.

## AT-31 Self-contained Initial Prompt

Wenn ein Initial Research Prompt erzeugt wird
Dann enthält er Search Profile, Constraints, Stichtag, aktive Criteria, vollständige Output-Struktur, kontrollierte Vokabulare und Provenienzregeln
Und verweist nicht auf lokale Repository-Pfade.
## AT-32 bis AT-36: Persönliche Triage

- AT-32: Ein gültiger persönlicher Wert wird gespeichert und ist im Detail getrennt vom externen Assessment sichtbar.
- AT-33: Eine Revision erzeugt einen neuen Datensatz mit Vorgängerreferenz; die alte Revision bleibt abrufbar.
- AT-34: Ungültige Werte und leere Exclusion-Gründe werden abgelehnt, ohne Daten zu schreiben.
- AT-35: Exclusion, Statusänderung und Restore erzeugen chronologische Decision History; Restore erfordert eine aktive Exclusion.
- AT-36: Ein erneuter Research-Import verändert persönliche Assessments, Decisions und Tracking Status nicht.
