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

Gegeben ein bekanntes Posting mit Source und deterministischer Identität
Wenn ein Update dieselbe externe Posting-ID liefert oder die normalisierte HTTPS-URL als Fallback verwendet
Dann wird keine zweite Posting Entity erzeugt.

## AT-05 Unsichere Dublette

Gegeben zwei ähnliche Postings ohne sicheren Identifier  
Wenn sie importiert werden  
Dann wird kein automatischer Merge durchgeführt  
Und ein Duplicate Case wird angelegt.

## AT-06 Availability

Gegeben eine bisher erreichbare Anzeige  
Wenn ein Availability Check `explicitly_unavailable` meldet
Dann bleibt das Posting historisch erhalten  
Und die aus Observations abgeleitete Availability wird nachvollziehbar geändert.

## AT-07 Temporärer Fehler

Wenn eine Source nur `temporarily_unreachable` ist  
Dann wird die Availability `uncertain` und die Opportunity nicht als definitiv geschlossen markiert.

## AT-08 Prompt Initial Research

Wenn der Nutzer einen Initial Research Prompt erzeugt  
Dann enthält der Prompt die gewünschte Bundle Version, das reine JSON-Ausgabeformat und keine nicht benötigten Bestandsdaten.

## AT-09 Prompt Full Update

Wenn ein Full Update Prompt erzeugt wird  
Dann enthält er Vocation-issued opaque Correlation References, offene Unsicherheiten und den erlaubten Änderungsumfang
Und enthält im v0.3 keine Availability/Freshness.

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
Dann ist dies in der Kartenansicht erkennbar; Vocation liefert die Precision als fachliche Information an die generische Orientation-Darstellung.

## AT-15 Spatial Feature öffnet Detail

Wenn der Nutzer ein räumliches Feature auswählt und die von Vocation bereitgestellte Detail-Aktion aktiviert  
Dann wird die Vocation-Vorschau oder Detailansicht geöffnet  
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

## AT-21 Published Cross-device Read

Wenn Wiiii Got This eine Published Vocation Capability verwendet
Dann ist sie read-only und enthält keine Import- oder Decision-Commands.

## AT-22 Publication Snapshot Age

**Späteres Slice-Verhalten, nicht v0.3.**

Wenn eine Publication Snapshot älter ist
Dann zeigt der Client Publication Age, ohne daraus stale oder unavailable Job Postings abzuleiten.

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

## AT-50 Explicit version dispatch

Der Import dispatcht Research Bundle `1.0` ausschließlich als initial-only und Research Update Bundle `2.0` ausschließlich als kontrolliertes Update.

## AT-51 Planner blockers before mutation

Unbekannter Prompt Context, Scope-/Correlation-Fehler und deterministische Identity-Konflikte werden im Update-Plan vor jeder Domain-Mutation als Blocker gemeldet.

## AT-52 Safe reuse and append-only evidence

Ein akzeptiertes Update verwendet bestehende Company-, Opportunity- und Posting-Subjects wieder, schreibt deren kanonische Zustände nicht um und speichert neue Sources, Source References und externe Evidence append-only.

## AT-53 Atomic rollback, personal-state preservation and idempotency

Ein vor `Apply` erkannter Blocker verursacht keinerlei Domain-Mutation. Eine Exception während der atomaren `Apply`-Transaktion rollt alle Update-Schreibvorgänge zurück. Persönliche Assessments, Decisions und Tracking Status bleiben unverändert. Ein bereits angewendeter identischer Update-Fingerprint wird nicht erneut angewendet.

## AT-54 Duplicate Case create/reuse without mutation

Possible-Duplicate-Evidence erzeugt oder verwendet ausschließlich einen ungelösten Duplicate Case. Es findet kein Merge, keine Löschung und keine kanonische Umschreibung statt.

## AT-55 Minimale Prompt Context Scopes

Full-, Company-, Opportunity- und Gap-Filling-Prompt Contexts enthalten ausschließlich ihren erlaubten Scope; sie enthalten keine unabhängigen Subjects außerhalb des Scopes und keinen persönlichen Zustand.

## AT-56 Gap-Filling-Minimierung

Ein Gap-Filling-Prompt Context enthält ausschließlich die ausdrücklich angeforderten Subject-/Observation- oder Criterion-Kombinationen.

## AT-57 Prompt Context Traceability

Ein Update PromptRun persistiert genau einen Prompt Context Snapshot und dessen Prompt Context Ref. Ein angewendeter Update-Import persistiert die validierte Ref und Bundle Version 2.0, während Initial Research außerhalb dieser Beziehung bleibt.

## AT-58 Typed Update API

Die typisierten Update-Endpunkte und OpenAPI-Verträge sind verfügbar; der Initial-Research-Endpunkt bleibt kompatibel.

## AT-59 Desktop Update Workflow

Für alle fünf Modi unterstützt die Desktop-UI Scope-Auswahl, Prompt-Generierung, Preview, Copy/Save und Inline-Import des zurückgegebenen JSON. Ein neuer Preview ersetzt einen veralteten Preview-Inhalt.

## AT-60 Update Import Traceability

Ein erzeugtes Update Bundle kann über den v0.3-Importer aus Issue #9 importiert werden; Duplicate-Importe erzeugen keine neue Mutation und bewahren die ursprünglichen Bundle-, Prompt- und Prompt-Context-Metadaten.

## AT-61 WGT iPhone ohne Windows-PC

Wenn der Windows-PC ausgeschaltet ist
Dann kann Wiiii Got This die letzte veröffentlichte Read Projection auf dem iPhone anzeigen.

## AT-62 Local-only Operation

Wenn keine Remote-Publikation konfiguriert ist
Dann bleiben lokale Prompting-, Import-, Pflege- und Read-Workflows nutzbar.

## AT-63 Opportunity Overview 1.0 Contract

Das Artefakt validiert gegen `schemas/published-opportunity-overview-v1.schema.json`; Capability und Contract Version sind exakt `vocation.opportunity_overview` und `1.0`.

## AT-64 Published Field Exclusions

Das Artefakt enthält keine geschützten persönlichen, internen Import-/Provenance-, Prompt-, Observation-, URL-, Availability/Freshness- oder Schreibfelder; unbekannte Properties werden abgelehnt.

## AT-65 Opaque Published References

`opportunity_ref`, `company_ref` und `publication_ref` sind nichtleere opaque Vocation-Referenzen. Verbraucher dürfen sie speichern und zurückgeben, aber nicht interpretieren.

## AT-66 Deterministic Opportunity Overview

Vocation erzeugt Opportunities und Work Locations in der eingefrorenen deterministischen Reihenfolge; die Reihenfolge ist für stabile Snapshots und Tests bestimmt, aber nicht fachlich semantisch.

## AT-67 Empty Published Market

Ein gültiges Opportunity-Overview-Artefakt darf eine leere `opportunities`-Liste enthalten.

## AT-68 Publication Age versus Freshness

Das Artefakt enthält `generated_at`, aber weder `publication_age` noch `stale`. Consumer können daraus Publication Age ableiten; daraus darf keine Vocation Availability/Freshness abgeleitet werden.

## AT-69 Availability Check Bundle 1.0

Ein Availability Check Bundle 1.0 validiert nur mit `bundle_kind: "availability_check"`, `bundle_version: "1.0"`, Prompt Context Ref, Availability Scope, mindestens einer Observation und den fünf eingefrorenen Result-Werten.

## AT-70 Append-only Availability Observations

Ein akzeptierter Availability Check ergänzt AvailabilityObservations append-only. Ein Blocker erzeugt keine Observation-Writes und keine persönlichen Änderungen.

## AT-71 AvailabilityEvaluator

Die neueste Observation mappt deterministisch auf `available`, `unavailable`, `uncertain` oder `unknown`. `temporarily_unreachable`, `not_found` und `indeterminate` ergeben `uncertain`, nie definitiv `unavailable`.

## AT-72 Opportunity Availability Aggregation

Opportunity Availability ist `available`, wenn ein Posting verfügbar ist; sonst `uncertain`, wenn eines unsicher ist; sonst `unknown`, wenn eines unbekannt ist; nur bei vorhandenen und ausschließlich nicht verfügbaren Postings `unavailable`. Ohne Postings ist sie `unknown`.

## AT-73 Personal-state Preservation

Availability Checks verändern weder Tracking Status, Personal Assessments, Decisions, Exclusion/Restore noch Groups/Waves.

## AT-74 Availability-evidence Freshness

Posting- und Opportunity-Read-Models leiten `last_checked_at` und nichtnegative `age_days` aus der neuesten Availability Observation und einer injizierten UTC-Uhr ab. Freshness ist keine Availability-Änderung.

## AT-75 Availability Prompt und interne API

Availability Check Prompt-Erzeugung, dedizierte Availability-Import-Routen, Availability/Freshness-Felder in den internen Opportunity- und Posting-Read-Models sowie die React/Desktop-Integration sind implementiert. Die Liste bietet Filter und Badges; die Detailansicht zeigt Status und Historie. Der Published Opportunity Overview 1.0 Contract bleibt unverändert.

## AT-76 No Automatic Stale Threshold

Es gibt keine Fresh-/Stale-Kategorie und keinen automatischen Ablauf. Alte explizit verfügbare Evidenz bleibt `available`, während ihr Alter separat angezeigt wird.

## AT-77 Research Update Compatibility

Research Update Bundle 2.0 bleibt unverändert; Availability-Felder, Availability-Scope und Availability-Observation-Typen werden nicht in diesen Vertrag aufgenommen.

## AT-78 Opportunity Groups and Application Waves

Eine Group besitzt stabile ID, nichtleeren Namen, optionale Beschreibung und Type `general` oder `application_wave`; Application Wave ist kein separates Aggregate.

## AT-79 Ordered Membership and Group Commands

Memberships sind durch `(group_id, opportunity_id)` eindeutig und besitzen explizite Positionen. Add hängt an, Remove betrifft nur die Group, Reorder normalisiert den vollständigen Satz deterministisch, Delete löscht keine Opportunity.

## AT-80 Group State Isolation

Groups/Waves verändern weder Opportunity-Zustand, Tracking Status, Personal Assessments, Decisions, Availability/Freshness noch Research-Daten. Research- und Availability-Bundles können keine Memberships erzeugen oder ändern.

## AT-81 Group Reads and Filtering

Group list/detail, geordnete Opportunities, Membership-Anzeige in Opportunity List/Detail sowie `group_id`-Filter sind implementiert. Die React Groups & Waves UI und `/api/groups` unterstützen diese Read-Capabilities.

## AT-82 MapLocationResolution

Eine WorkLocation kann durch explizite Nutzeraktion höchstens eine aktuelle MapLocationResolution mit gültigen Koordinaten, `manual` oder `geocoder`, optionalem Provider Key, Zeitpunkt und verwendeter Query/Label besitzen. Die Persistence und UI-Aktionen für Geocode, Manual und Delete sind implementiert. Ohne Resolution ist sie `unmapped`; WorkLocation Evidence und Precision bleiben unverändert.

## AT-83 MapProjection and Filter Consistency

Die implementierte interne MapProjection erzeugt ein Feature pro aufgelöster WorkLocation aus einer expliziten Opportunity-ID-Menge. `/api/map`, gemeinsame List/Map-Filter, Tracking Status, Availability und Group/Wave-Memberships werden nur gelesen und repräsentieren dieselben gefilterten Opportunities.

## AT-84 Desktop Map Boundary

Die implementierte Kartenansicht nutzt `OrientationMapFrame` und den gepinnten Orientation Embed Host über `orientation.host-bridge` 1.0 statt eines Vocation-eigenen Leaflet-Renderers. Vocation liefert die fachliche MapProjection, Information Rows und opaque Action References; Orientation besitzt generisches Rendering, Clustering und Hit Testing. Aktivierte Actions werden an Vocation zurückgegeben und dort fachlich interpretiert. Es gibt keine automatische oder periodische Geocodierung, keine automatische externe URL-Navigation und keine Mutation von Opportunity-, Personal-, Research- oder Availability-Zustand. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben unverändert.

## AT-85 ExternalLinkPolicy

ExternalLink ist ein abgeleiteter Read-Wert ohne eigene Tabelle. Nur absolute `https`-URLs mit nichtleerem Host sind gültig; andere, malformed oder relative URLs werden lokal abgelehnt und erreichen keinen Browser Adapter.

## AT-86 PreferredPostingSelector

Gültige Links werden deterministisch nach Availability, Source Type, neuestem `observed_at` und Posting ID gerankt. Explizite Posting-/Source-Auswahl gilt nur für die aktuelle Aktion; es gibt keine persistierte persönliche Präferenz.

## AT-87 Explicit Navigation

`OpenPostingInBrowser` öffnet ausschließlich nach expliziter Nutzeraktion über einen austauschbaren Browser Adapter. Laden, Filtern, Detail- oder reine Spatial-Feature-Auswahl öffnen keinen Browser; erst eine von Vocation definierte External-Link-Action darf den bestehenden Vocation-Command auslösen. Availability und persönlicher Zustand bleiben unverändert.

## AT-88 URL-Free MapProjection

Die MapProjection enthält keine URLs oder `posting_links`. Vocation ermittelt ExternalLink-Kandidaten separat über Opportunity ID und kann daraus opaque Action References für die lokale Orientation Spatial Scene ableiten; URLs werden nicht Teil der Projection. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben URL-frei.

## AT-89 External Navigation Workflow

Die implementierten `/api/external-links`-Read-/Open-Endpunkte, typed Clients und Opportunity-Detail-UI zeigen Source, Availability, Observed At und Preferred-Marker. Default-/Preferred- sowie explizites Posting-Öffnen, No-Link- und lokale Browser-Fehlerzustände sind abgedeckt. Für die Kartenansicht lädt Vocation Kandidaten separat und dedupliziert pro Opportunity; die Orientation-Darstellung erhält nur Vocation-definierte Informationen/Action References und eine Action-Aktivierung wird anschließend von Vocation ausgeführt.

## AT-90 Comparison Selection

Die implementierte `Vergleichen`-UI und `POST /api/comparison/opportunities` akzeptieren genau 2 bis 4 eindeutige, existierende Opportunity IDs, behalten deren angeforderte Reihenfolge und lehnen Duplikate, falsche Anzahl oder fehlende Opportunities ohne stille Auslassung ab. Die Auswahl wird nicht persistiert.

## AT-91 Opportunity Comparison Read Model

Jede Vergleichsspalte zeigt Opportunity/Company, WorkLocations mit Precision, Tracking Status, Availability mit Availability-evidence Freshness sowie kompakte Group/Wave-Memberships. Das implementierte Read Model ist intern, read-only, horizontal scrollbar für 2–4 Spalten und enthält keine URLs oder Browser-Aktionen.

## AT-92 Research Evidence Comparison

Die sechs festgelegten Research-Dimensionen verwenden nur Opportunity- und Posting-scoped Observations. Fehlende Daten sind `missing`; mehrere Werte bleiben deterministisch als Evidenz sichtbar und werden nicht automatisch als widersprüchlich bezeichnet. Company-scoped Observations werden nicht kopiert.

## AT-93 Assessment Comparison and State Isolation

Opportunity-scoped Assessments werden criterion-keyed verglichen; Personal Assessments zeigen nur die aktuelle Revision, External Assessments mehrere Werte ohne automatische Auswahl. Die typed Clients und die Navigation zu bestehenden Vocation Details sind implementiert. Comparison verändert weder Tracking Status, Groups/Waves, Assessments noch Decisions. Risk bleibt ohne konkrete Read-Quelle außerhalb der V1-Ansicht.

## AT-94 Published Map Projection 1.0 Contract

Das kanonische Artefakt validiert gegen `schemas/published-map-projection-v1.schema.json` mit Capability `vocation.map_projection`, Contract Version `1.0`, Publication Metadata und geschlossenen Feature-Objekten. Leere `features` sind gültig.

## AT-95 Published Map Projection Boundaries

Jedes Feature enthält nur opaque Refs, Titel, Company, WorkLocation Label/Precision und Latitude/Longitude. Nur vorhandene explizite MapLocationResolutions erzeugen Features; mehrere mapped WorkLocations derselben Opportunity sind erlaubt. Es gibt keine URLs, Navigation, persönliche oder Research-Daten, Availability/Freshness, Groups/Waves, Provider-/Query-/Resolved-at-Metadaten oder Schreibbefehle.

## AT-96 Published Map Projection Runtime

`GET /published/v1/map-projection` liefert die implementierte Published Map Projection 1.0 außerhalb der internen React OpenAPI. Ein dedizierter read-only Publication Repository/Service veröffentlicht ausschließlich bestehende MapLocationResolutions, geocodiert und mutiert nie, akzeptiert eine leere Projection und ordnet Features deterministisch nach Company Name, Opportunity Title, WorkLocation Label case-insensitiv und `feature_ref`. Published Opportunity Overview 1.0 bleibt unverändert.

## AT-97 ApplicationCase Ownership and Lifecycle

Die implementierte ApplicationCase-Domäne bindet einen Case an genau eine Opportunity, wird ausschließlich explizit erstellt und verwendet die Zustände `draft`, `ready`, `submitted`, `interviewing`, `offer`, `accepted`, `rejected` und `withdrawn`; die letzten drei sind terminal. Lifecycle Events bleiben historisch lesbar und sind vom Opportunity Tracking Status getrennt.

## AT-98 ApplicationCase Isolation

Die implementierte Persistenz und History erzwingen höchstens einen aktiven/nonterminal Case je Opportunity. Research-/Availability-Imports und Groups/Waves erzeugen oder ändern keine ApplicationCases. Es gibt keine automatische Submission oder Transition aus E-Mail, Kalender oder externen Quellen.

## AT-99 Private ApplicationMaterial Boundary

ApplicationMaterial-Metadaten verwenden die Arten `cv`, `cover_letter` und `other` sowie explizite historische Revisionen; aktuelle Metadaten und die aus der Revision-Historie rekonstruierte aktuelle Revision sind implementiert. Private Inhalte erscheinen weder in Published Contracts, öffentlichen Fixtures, Logs, Research-/Availability-Bundles noch Publication Endpoints. Opportunity Overview 1.0 und Map Projection 1.0 bleiben unverändert.

## AT-100 ApplicationCase API and UI

Die internen ApplicationCase-/Material-Endpunkte, der typed Client und das Opportunity-Detail-React-Panel sind implementiert. Unterstützt werden Case-Liste/Detail, Lifecycle, Material-Metadaten und Material-Revisionen. Ein vollständiger Material-History-Endpoint existiert weiterhin nicht. Dokument-Payloads und Storage-Referenzen werden nicht in das normale ApplicationCase Read Model eingebettet; die separaten privaten ApplicationDocument-Endpunkte aus Slice 16/17 existieren daneben ausdrücklich.

## AT-101 ApplicationDocument Semantics

Die implementierte Material-Revision kann null oder ein immutable ApplicationDocument mit Document ID, Material ID/Revision, Original-Dateiname, erlaubtem Media Type, Byte Size, SHA-256 und Created At besitzen. Creation berechnet Byte Size und SHA-256 aus den gelieferten Bytes; Content-Ersatz erfolgt nur durch neue Material-Revision. Die Datenbank erzwingt `UNIQUE(material_id, material_revision)`; historische Revisionen behalten eigene Dokumente und neue Revisionen erben keine Dokumentdaten.

## AT-102 Document Privacy and Integrity Boundary

ApplicationDocument-Payload und identifizierende Metadaten erscheinen nicht in Published Contracts, Research-/Availability-Bundles, Prompt Contexts, Logs, Fixtures oder Publication Endpoints. Die implementierte Store-/Service-Kette schreibt create-only und atomic, liest Payloads zurück und erkennt fehlende oder korrupte Bytes als Integrity Errors; `storage_ref`, Pfade und hashed physical filenames werden nicht geleakt. Rendering, Editing/Generation, Encryption, Retention/Delete und Transport bleiben außerhalb der implementierten Dokument-Baseline bzw. benötigen eigene spätere Semantik.

## AT-103 Private Document API and React Upload

Die internen Multipart-Endpunkte für revisionsgebundene Dokumente, der typed Client und der Opportunity-Detail-Upload-Workflow sind implementiert. Erlaubt sind PDF, Plain Text und Markdown mit explizitem Media Type; Dateiname, Type, Byte Size und Created At werden angezeigt. Preview, Delete, Export/Download, Save-as und In-place-Replacement sind nicht implementiert; `Öffnen` ist als separater Slice-17-Workflow implementiert.

## AT-104 Slice 17 ApplicationDocument Access (implementiert)

Ein bereits angehängtes PDF kann nur nach expliziter Nutzeraktion `Öffnen` über `OpenApplicationDocument` gelesen werden. Die fokussierte React-Abdeckung verifiziert die Aktion nur bei angehängtem Dokument, die exakte Dokument-ID/Content-URL, neuen Browsing-Kontext sowie `noopener`/`noreferrer`. Der Zugriff verwendet genau `document_id` der aktuell angezeigten `(material_id, material_revision)` und liefert nach Byte-Size-/SHA-256-Prüfung die exakten Bytes mit dem persistierten Media Type. Es gibt keinen Fallback auf eine andere oder neueste Revision.

Ein bereits angehängtes `text/plain` kann explizit gelesen werden; dasselbe gilt für `text/markdown`, jeweils mit identischem Verhalten der privaten Content-Grenze. Die Abdeckung verifiziert außerdem, dass nach einer neueren Material-Revision keine ältere Dokumentrevision wiederverwendet wird. Ein angehängtes `text/markdown` liefert die exakt gespeicherten Bytes; Vocation führt keine Markdown-Transformation oder Rendering durch. Ohne angehängtes Dokument existiert keine Öffnen-Aktion.

Fehlende Dokument-Metadaten ergeben `document metadata not found`. Fehlende Backing Bytes oder korrupte Bytes ergeben einen expliziten Integrity Error; es wird kein leeres oder synthetisches Dokument zurückgegeben.

Öffnen verändert weder ApplicationCase-Lifecycle noch Opportunity Tracking Status und erzeugt keinen ApplicationMaterial- oder ApplicationDocument-Zustand. Die fokussierte UI-Abdeckung bestätigt das Fehlen von Replace-, Delete-, Download- und Preview-Aktionen sowie das Nicht-Leaken von Storage-Pfad/Reference; neue Backend-Tests wurden für Slice 17 nicht hinzugefügt. `storage_ref`, physische Pfade, hashed physical filenames und Store Root werden nie als Response ausgegeben. Payload und private Metadaten bleiben aus Published Opportunity Overview, Published Map Projection, Research-/Availability-Bundles, Prompt Contexts, öffentlichen Fixtures und Publication Endpoints ausgeschlossen.

## AT-105 Orientation Geospatial Integration Boundary

Eine explizite Vocation-Geocode-Aktion nutzt den Vocation `Geocoder`-Port mit `OrientationGeocoder` und ruft Orientation Place Search über `GET /api/v1/places/search` auf. Vocation ruft weder Nominatim noch Photon direkt auf. Ein fehlgeschlagener oder ungültiger Orientation-Response erzeugt einen sichtbaren Fehler und keine erfundenen Koordinaten oder stille Provider-Umschaltung; WorkLocation Evidence und Precision werden nicht verändert.

Die Vocation-Kartenansicht nutzt den gepinnten Orientation Embed Host über `orientation.host-bridge` 1.0. Vocation erzeugt/adaptiert die fachliche MapProjection, Information Rows und opaque Action References; Orientation rendert generisch und meldet Action-Aktivierungen zurück. Orientation liest keine Vocation-Datenbank und entscheidet nicht über Work Location, Precision, Opportunity, Availability, Preferred Posting oder Browsernavigation.

Die lokale Orientation-Komposition verändert weder Published Opportunity Overview 1.0 noch Published Map Projection 1.0. Weitere Orientation-Capabilities wie Routing werden nicht allein durch ihre Verfügbarkeit Bestandteil von Vocation, sondern benötigen einen konkreten Vocation-Nutzerfall und eine eigene Semantikentscheidung.

## AT-106 Duplicate Decision History and Isolation

Ein bestehender Opportunity- oder Posting-DuplicateCase kann nur durch explizite Nutzeraktion mit `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` oder `keep_unresolved` und nichtleerem Grund entschieden werden. Jede Decision wird mit fortlaufender Sequence append-only gespeichert; eine abweichende spätere Decision wird aktuell, ohne ältere Decisions zu verändern. Dasselbe aktuelle Outcome wird als Konflikt abgelehnt. Research-/Availability-Imports sowie persönliche Opportunity-Zustände bleiben davon unverändert.

## AT-107 Duplicate Review API and UI Without Merge

Die internen `/api/duplicate-cases`-Routen liefern Opportunity- und Posting-Cases mit lesbaren Subject-/Source-Summaries, aktueller Decision und Historie. Die React-Ansicht `Dubletten` filtert offen/entschieden/alle, verlangt einen Entscheidungsgrund und zeigt Evidence-URLs nur als nicht klickbaren Review-Kontext. `confirmed_duplicate` erzeugt weder Merge, Delete, Re-Parenting noch sonstige Identitätsmutation; es gibt keine Merge-/Delete-Controls und keine Änderung an Published Opportunity Overview 1.0 oder Published Map Projection 1.0.

