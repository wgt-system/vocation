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
## AT-32 Personal Assessment Create

Wenn für eine Opportunity und ein aktives Opportunity-Criterion ein Wert angelegt wird, entsteht genau eine aktuelle unveränderliche Revision.

## AT-33 Duplicate Create und immutable Revision

Ein zweites Create für dasselbe Opportunity/Criterion wird als Konflikt abgelehnt. Eine Revision erzeugt einen neuen Datensatz, verlinkt den Vorgänger und lässt die alte Revision sichtbar; eine alte Revision kann nicht erneut revidiert werden.

## AT-34 Criterion- und Value-Validation

Numeric-, Categorical-, Boolean- und Text-Werte werden jeweils typ- und skalenkonform validiert. Unbekannte oder inaktive Criteria sowie ungültige Werte werden atomar abgelehnt. Semantische Änderungen eines referenzierten Criteria werden abgelehnt.

## AT-35 Personal/External Separation

Ein Personal Assessment ist im Detail getrennt vom External Assessment sichtbar und wird nicht durch Importdaten ersetzt.

## AT-36 Tracking transitions

Die Statuswerte sind exakt `new`, `to_review`, `interesting`, `shortlisted`, `deferred`, `excluded`, `archived`. Normale nicht ausgeschlossene Übergänge sind direkt möglich; ein No-op und ein generischer Übergang zu `excluded` werden abgelehnt.

## AT-37 Exclusion

Exclusion ist eine eigene Operation, verlangt einen nichtleeren Grund, speichert den vorherigen Status und erzeugt einen unveränderlichen Decision-Eintrag.

## AT-38 Restore

Restore ist nur bei aktueller Exclusion erlaubt, referenziert die aktive Exclusion und verwendet ohne Zielstatus deren gespeicherten vorherigen Status. Ein expliziter gültiger nicht ausgeschlossener Zielstatus ist möglich; historische Exclusions bleiben unverändert. Wiederholte Exclusion/Restore-Zyklen referenzieren jeweils die korrekte aktive Exclusion.

## AT-39 Import Preservation

Ein wiederholter Research-Bundle-Import lässt aktuellen persönlichen Wert, alle Revisionen, Tracking Status und Decision History unverändert.

## AT-40 Status Filtering and Decision History

Die Stellenliste filtert nach Tracking Status; die Detailansicht zeigt die chronologische Decision History.

## AT-41 Triage UI

Die UI trennt Create und Revise, zeigt typisierte Assessment Controls, bietet Status-/Exclusion-/Restore-Aktionen und zeigt bei einem Mutationsfehler das bereits geladene Read Model weiter an.

## AT-42 Migration fresh install

Eine leere Datenbank migriert bis `head` und enthält die v0.2-Triage-Struktur.

## AT-43 Migration from v0.1.0

Eine auf `0002` migrierte v0.1.0-Datenbank migriert bis `head` und liefert dasselbe Schema wie die Fresh-Installation.

## AT-44 Migration integrity constraints

Das Schema schützt `UNIQUE(opportunity_id, criterion_id, revision_number)`, `UNIQUE(supersedes_id)`, `UNIQUE(reverses_decision_id)`, `revision_number >= 1` und `origin = 'personal'`.

## AT-45 Persistent restart

Nach Dispose und Neustart mit derselben SQLite-Datei bleiben Opportunity, Status, aktuelles Personal Assessment, beide Revisionen, vollständige Decision History und die Restore-Referenz erhalten.

## AT-46 Update contract compatibility

Research Bundle `1.0` validiert das unveränderte Initial-Beispiel und lehnt Update Scopes ab. Research Update Bundle `2.0` ist ein separater Contract.

## AT-47 Update scope modes

Full, Company, Opportunity und Gap Filling validieren jeweils mit `prompt_context_ref`; bekannte Subjects verwenden opaque Correlation References, neue Subjects Creation-/Evidence-Felder.

## AT-48 Closed and protected update objects

Unbekannte Properties und Personal-State-Properties werden abgelehnt. Gap Filling mit neuen Companies, Opportunities, Postings oder Possible Duplicates wird strukturell abgelehnt.

## AT-49 Update identity and duplicate evidence

Possible-Duplicate-Einträge sind nur Evidenz für Opportunity-/Posting-Paare mit Quellenbeleg; Company-Duplicates, Self-References und automatische Merge-Bedeutung sind unzulässig. Posting-Identität bleibt Source plus External ID oder HTTPS-URL; Correlation-/Identity-Konflikte sind Blocker.
