# Vocation – Domain Model

**Status:** Draft 0.2

## Aggregate Roots

### JobOpportunity

Zentraler persönlicher Bezugspunkt.

Wesentliche Felder:

- `OpportunityId`
- `CanonicalTitle`
- `CompanyId`
- optionale `OrganizationUnitId`
- `WorkLocations`
- `TrackingStatus`
- optionale `Priority`
- Zeitpunkte

Invarianten:

- genau eine aktive Company-Zuordnung,
- `excluded` benötigt aktive Exclusion Decision,
- External Imports verändern keine Personal Decisions,
- mehrere Postings sind erlaubt,
- Archivierung löscht keine Historie.

### JobPosting

Konkrete Veröffentlichung.

Wesentliche Felder:

- `PostingId`
- `SourceId`
- `SourceReference`
- optionale External ID
- beobachteter Titel
- `FirstObservedAt`
- `LastObservedAt`
- optionale `OpportunityId`

Regeln:

- genau eine Source,
- sichere Opportunity-Zuordnung oder explizite Unsicherheit,
- URL-Wechsel ändert nicht automatisch Identität,
- externe Links werden separat validiert.

### Company

- `CompanyId`
- Canonical Name
- Alternative Names
- Official Website
- Locations
- Organization Units

### ResearchImport

- `ImportId`
- Bundle Fingerprint
- Bundle Version
- Status
- Entry Results
- Errors und Warnings

### ResearchPromptRun

Dokumentiert die Erzeugung eines konkreten Prompts.

Felder:

- `PromptRunId`
- `PromptType`
- `PromptVersion`
- `BundleVersion`
- as-of date
- criteria snapshot
- rendered prompt
- Initial: Search Profile / Constraints
- Update: Prompt Context Ref

Regeln:

- PromptRun verändert keine Domänendaten,
- Scope ist explizit,
- ein Update PromptRun hat genau eine nicht-null `Prompt Context Ref`; ein Initial PromptRun hat keine Prompt Context Ref,
- der PromptContextSnapshot ist der Traceability-Pivot und enthält read-only Kontext,
- Ausgabeanforderung verweist auf eine Bundle Version.

### OpportunityAssessment

Historische Bewertung mit Origin, Type, Dimensions, Result und Reasoning.

Im ersten Meilenstein referenziert jedes externe Assessment genau ein Vocation-eigenes `AssessmentCriterion`. Externe Bundles dürfen keine Kriterien definieren.

### AssessmentCriterion

Vocation-eigener Kriterienkatalog mit stabiler Criterion ID, Display Name, Beschreibung, Value Type (`numeric`, `boolean`, `categorical`, `text`), optionalem Zahlenbereich oder erlaubten Kategorien, Applicable Subject Type, Aktivierungszustand und Display Order.

Nach dem ersten referenzierenden Assessment dürfen Value Type, Skala/Kategorien und Applicable Subject Type nicht inkompatibel geändert werden. Dafür muss eine neue Criterion ID angelegt werden. Name, Beschreibung, Aktivierung und Reihenfolge bleiben editierbar.

### OpportunityDecision

Bewusste persönliche Entscheidung mit Reason und möglicher Reversal-Beziehung.

### ApplicationCase

Vocation-owned Aggregate mit stabiler `ApplicationCaseId`, referenziert genau eine `OpportunityId` und besitzt einen ApplicationCase-Lifecycle sowie historische Lifecycle Events. V1-Lifecycle: `draft`, `ready`, `submitted`, `interviewing`, `offer`, `accepted`, `rejected`, `withdrawn`; `accepted`, `rejected` und `withdrawn` sind terminal.

Invarianten:

- Erstellung und Lifecycle-Änderungen erfolgen ausschließlich durch explizite Nutzeraktionen.
- Eine Opportunity hat höchstens einen aktiven/nonterminal ApplicationCase; terminale Cases bleiben historisch lesbar.
- `Opportunity.tracking_status` bleibt unabhängiger Triage-Zustand und wird nicht vom ApplicationCase überschrieben.
- Research-/Availability-Imports und Groups/Application Waves erzeugen oder verändern keine ApplicationCases.
- Keine automatische Submission oder Transition aus E-Mail, Kalender, Research, Availability oder externen Quellen.

### ApplicationMaterial

Private, von einem ApplicationCase besessene Metadaten-Entity mit `MaterialId`, `ApplicationCaseId`, Kind `cv`, `cover_letter` oder `other`, Display Name, Revision sowie Created/Updated Timestamps. Revisionen sind explizit und historisch. Inhalt, Dateiformat, Speicherort, Rendering und Verschlüsselung sind nicht Teil dieses Slice.

### ApplicationDocument

Private Content-Entity an genau einer immutable ApplicationMaterial-Revision. Felder: `DocumentId`, `MaterialId`, `MaterialRevision`, Original Display Filename, Media Type, Byte Size, SHA-256 Content Digest und `CreatedAt`. Pro Material-Revision gibt es null oder ein Dokument. Erlaubte Media Types sind `application/pdf`, `text/plain` und `text/markdown`. Payload ist nach dem Anhängen unveränderlich; Content-Ersatz erfordert eine neue Material-Revision. Fehlende gespeicherte Bytes sind ein expliziter Integrity Error.

`ApplicationDocumentStore` ist ein Infrastruktur-Port mit opaque Storage Reference. Keine automatische Deduplication, keine gemeinsame Ownership und keine Löschung aufgrund gleicher SHA-256-Werte.

### OpportunityGroup

Aggregate mit stabiler `GroupId`, nichtleerem Namen, optionaler Beschreibung, Type `general` oder `application_wave` und geordneten Memberships. `ApplicationWave` ist ausschließlich eine OpportunityGroup mit Type `application_wave`.

Membership enthält `GroupId`, `OpportunityId` und eine explizite Position. `(group_id, opportunity_id)` ist eindeutig. Eine Opportunity darf mehreren Groups und mehreren Application Waves angehören; es gibt weder Exklusivität noch eine Active-Wave-Invariante.

Invarianten und Commands:

- `CreateOpportunityGroup` erzeugt keine Änderung an einer Opportunity.
- `AddOpportunityToGroup` hängt eine Membership ans Ende an.
- `RemoveOpportunityFromGroup` betrifft nur die Membership der Group.
- `ReorderOpportunityGroup` erhält den vollständigen geordneten Member-Satz und normalisiert Positionen deterministisch.
- `DeleteOpportunityGroup` löscht Memberships, niemals Opportunities oder deren Zustand.
- Group Membership ist veränderbarer Organisationszustand und keine append-only Decision-Historie.
- Groups/Waves verändern niemals Tracking Status, Personal Assessments, Decisions, Availability/Freshness oder Research-Daten.
- Research- und Availability-Bundles dürfen Groups/Waves weder erzeugen noch verändern.
- V1 enthält keine Bewerbungseinreichung, Frist, Application Status oder automatische Statusübergänge.

### DuplicateCase

Im v0.3 ausschließlich eine ungelöste mögliche Identitätsbeziehung mit Evidenz. Es gibt noch keinen bestätigten, gelösten oder Merge-Zustand. Zukünftige Duplicate Decisions (`confirmed duplicate`, `confirmed distinct`, `related but distinct`, `keep unresolved`) bleiben spätere Domänenentscheidungen.

## Entities und Value Objects

- `ResearchObservation`
- `AvailabilityObservation`
- `Location`
- `WorkLocation`
- `Source`
- `SourceReference`
- `AssessmentScore`
- `Risk`
- `ExclusionReason`
- `PromptScope`
- `PromptContextSnapshot`
- `ExternalLink`
- `MapFeature`
- `MapLocationResolution`

### MapLocationResolution

Supporting Data im Vocation Context für eine `WorkLocation`, mit `WorkLocationId`, Latitude, Longitude, `ResolutionSource` (`manual` oder `geocoder`), optionalem `ProviderKey`, `ResolvedAt` und verwendeter Query/Label. Koordinaten sind auf Latitude -90..90 und Longitude -180..180 begrenzt; pro WorkLocation existiert höchstens eine aktuelle Resolution.

Eine erfolgreiche explizite Neuauflösung ersetzt die bisherige abgeleitete Resolution. Die Daten sind weder append-only Research Evidence noch Decision History. Keine Resolution bedeutet `unmapped`, nicht eine ungültige WorkLocation. Geocoding verändert weder WorkLocation noch deren Precision. Auflösung erfolgt ausschließlich explizit durch den Nutzer; automatische oder periodische Geocoding-Läufe gibt es nicht. Geocoder werden über einen provider-neutralen Port angebunden.

## ResearchPromptRun

### Prompt Types

- `initial_market_research`
- `full_update`
- `company_update`
- `opportunity_update`
- `gap_filling`
- `availability_check`
- `custom_subset`

Weitere nicht implementierte Prompt-Typen sind spätere Slices. `availability_check` ist auf `dev` implementiert und bleibt als post-v0.3 Workflow fachlich getrennt.

### Prompt Scope

Enthält:

- Scope Type
- referenzierte, für den Prompt Run erzeugte opaque Correlation References
- gewünschte Felder oder Fragen
- erlaubten Änderungsbereich
- Stichtag
- erwartete Bundle Version

### Invarianten

1. Ein Update-Prompt muss den Scope und einen Prompt Context Snapshot mit opaque Correlation References enthalten; interne Vocation IDs werden nicht veröffentlicht.
2. Ein Prompt darf nicht behaupten, selbst recherchiert zu haben.
3. Ein Prompt muss die gewünschte Ausgabe als reines JSON verlangen.
4. Ein Teilupdate darf keine außerhalb des Scopes liegenden Änderungen als verbindlich ausgeben.
5. Templates enthalten generische Schutzregeln; persönliche Assessments, Decisions und Tracking Status sowie deren Werte werden nicht in den öffentlichen Prompt Context eingebettet.

Für v0.3 sind Update Bundles ein eigener Published Contract `2.0`. Eine Correlation Reference gilt nur für den ausstellenden Prompt Context Snapshot und kann zwischen Prompt Runs wechseln. Sie löst genau ein bestehendes Company-, Opportunity- oder Posting-Objekt auf, erlaubt aber keine Änderung bestehender Ownership-Beziehungen.

`PromptContextSnapshot` ist der Traceability-Pivot und besitzt seinen eigenen Fingerprint. Ein Update PromptRun gehört genau zu einem Snapshot; ein Initial PromptRun hat keine Prompt Context Ref. Ein angewendeter Update-`ResearchImport` speichert `bundle_version = 2.0` und die validierte `prompt_context_ref`; ein initialer `1.0`-Import speichert keine Prompt Context Ref. `ResearchImport` referenziert niemals direkt einen `prompt_run_id`; mehrere Importe dürfen denselben Snapshot referenzieren.

## ExternalLink (implemented read/application value)

Derived Application/Read Value aus bestehendem Posting, Source und SourceReference; keine eigene Persistence-Tabelle.

Mindestfelder: `posting_id`, `source_id`, `source_name`, `source_type`, `url`, `display_label`, Posting Availability, `observed_at`, `preferred`.

Regeln:

- nur absolute `https`-URLs mit nichtleerem Host,
- `http`, `file:`, `javascript:`, `data:` und proprietäre/unbekannte Schemes sowie malformed/relative URLs ablehnen,
- lokale strukturelle Validierung ohne Fetch, HEAD-Check, Crawling oder URL-Probing,
- Posting Availability wird angezeigt, definiert aber nicht URL-Gültigkeit,
- nur nach expliziter Nutzeraktion öffnen; ungültige Links erreichen nie den Browser Adapter.

## Domain Services

### OpportunityIdentityResolver

Bewertet Matches und erzeugt Evidenz.

### ObservationReconciler

Leitet aktuelle Sichten aus Observations ab.

### AssessmentResolver

Wählt darzustellende Assessments ohne sie zu verändern.

### AvailabilityEvaluator

Leitet Availability aus Observations ab.

### ImportTranslator

Anticorruption Layer für Research Bundles.

Der erste Meilenstein verwendet ausschließlich deterministische Posting-Identität aus Source plus External Posting ID oder ersatzweise normalisierter HTTPS-URL. Fuzzy Matching ist nicht enthalten.

### PromptContextBuilder

Erzeugt den minimal nötigen Kontext für einen Prompt Scope.

### PreferredPostingSelector

Wählt für eine Ansicht bevorzugte gültige Posting-Links anhand dokumentierter Regeln:

1. Availability `available > unknown > uncertain > unavailable`,
2. Source Type `company_careers > job_board > professional_network > other`,
3. neuestes Posting `observed_at`,
4. Posting ID als deterministischer Tie-Break.

Eine explizite Posting-/Source-Auswahl überschreibt die Auswahl nur für die aktuelle Aktion und wird nicht persistiert. Der Selector mutiert weder Availability noch Posting-Zustand; ohne gültigen Link gibt es keinen Preferred Link.

### ExternalLinkPolicy

Validiert absolute HTTPS-URLs lokal strukturell und entscheidet, ob ein Link geöffnet werden darf. Der Browser Adapter ist austauschbare Infrastruktur.

Die implementierte SQLAlchemy-Read-Adapter liefert ExternalLink-Kandidaten ohne eigene Persistenz. `SystemBrowserAdapter` öffnet ausschließlich bereits validierte URLs im Standardbrowser des Betriebssystems.

## Domain Events

- `ResearchPromptGenerated`
- `ResearchImportCompleted`
- `ResearchImportRejected`
- `JobOpportunityCreated`
- `JobPostingCreated`
- `ResearchObservationRecorded`
- `OpportunityAssessmentAdded`
- `OpportunityExcluded`
- `OpportunityTrackingStatusChanged`
- `PossibleDuplicateDetected`
- `AvailabilityAssessmentChanged`
- `ExternalPostingOpened`

`ExternalPostingOpened` kann als Audit-/Analytics-Event behandelt werden, ohne die Fachidentität zu verändern.

## Repository-Grenzen

- `JobOpportunityRepository`
- `JobPostingRepository`
- `CompanyRepository`
- `ResearchImportRepository`
- `ResearchPromptRunRepository`
- `OpportunityAssessmentRepository`
- `OpportunityDecisionRepository`
- `OpportunityGroupRepository`
- `DuplicateCaseRepository`

## Read Queries

- `JobListQuery`
- `JobDetailQuery`
- `OpportunityComparisonQuery`

### OpportunityComparisonQuery (implemented read query)

Read-only Query für 2 bis 4 eindeutige, existierende Opportunity IDs in der angeforderten Reihenfolge. Sie erzeugt keine Domain-Mutation und keine Persistenz. Alle ausgewählten Opportunities müssen existieren; fehlende IDs führen zu einem Fehler statt stiller Auslassung. Es gibt kein Ranking, Scoring, keinen Winner und keine persistierte Shortlist.

Die Query vergleicht Opportunity- und zugehörige Posting-Observations nur in den sechs Dimensionen `technology_requirement`, `task`, `seniority`, `experience_requirement`, `work_model` und `salary`. Company-scoped Observations/Assessments werden nicht in Opportunity-Zellen kopiert. Opportunity-scoped Personal- und External-Assessments werden nach Assessment Criterion dargestellt; Personal Assessments verwenden nur die aktuelle Revision, ohne Historie. Mehrere Werte bleiben als Evidenzwerte sichtbar und werden nicht aus unterschiedlichen Strings automatisch als Widerspruch abgeleitet. Eine strukturierte Contradiction wird nur übernommen, wenn sie bereits explizit als solche vorliegt.
- `CompanyOverviewQuery`
- `MapProjectionQuery`
- `PromptContextQuery`
- `ImportReportQuery`
- `PublishedOpportunityOverviewQuery`

### Data Publication

Data Publication ist eine Vocation-owned Supporting Subdomain/Application Responsibility. Ein Publication Adapter erzeugt client-neutrale, versionierte Published Read Projections und Publication Snapshots. Die lokale Datenbank bleibt autoritativ; Publication Metadata und Snapshot Age sind abgeleitete Informationen und nicht Domain Freshness.

Für `Opportunity Overview` Published Contract 1.0 sind ausschließlich Capability, Contract Version, Publication Metadata (`publication_ref`, `generated_at`) und die geschlossenen Opportunity-Overview-Felder vorgesehen. Referenzen bleiben opaque; der Vertrag enthält keinen persönlichen Zustand, keine Import-/Provenance-Daten, keine URLs, Availability/Freshness oder Schreibinformationen.

Availability Check Bundle 1.0 bleibt ein separater Vertrag. `AvailabilityObservation`-Einträge sind append-only Evidenz; aktuelle Posting-/Opportunity-Availability und availability-evidence Freshness werden daraus abgeleitet und verändern keinen persönlichen Zustand.
## Persönliche Triage

`Opportunity.tracking_status` gehört zur Vocation-Opportunity und wird ausschließlich durch persönliche Commands geändert. `PersonalAssessment` enthält Opportunity, Criterion, Wert, Begründung, Erstellzeitpunkt, Revisionsnummer und `supersedes_id`; Datensätze sind append-only, pro Opportunity/Criterion gibt es genau eine aktuelle Revision. `OpportunityDecision` enthält vorherigen und resultierenden Status, Typ, optionalen Grund und bei Restore die Referenz auf die aktive Exclusion.

Invarianten: neue und revidierte Assessments verwenden nur aktive Opportunity-Kriterien und gültige Numeric-, Categorical-, Boolean- oder Text-Werte; nur die aktuelle Revision darf revidiert werden; Create ist für ein bereits vorhandenes Opportunity/Criterion unzulässig; Exclusion benötigt einen Grund; Restore ist nur für ausgeschlossene Opportunities zulässig und löst den Default aus dem gespeicherten vorherigen Status auf; Import verändert weder PersonalAssessment noch Decision oder Tracking Status. Application Services hängen ausschließlich von Repository-Ports ab.
