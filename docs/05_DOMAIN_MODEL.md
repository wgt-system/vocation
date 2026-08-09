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
- `PromptTemplateId`
- `PromptVersion`
- `PromptScope`
- `GeneratedAt`
- `ContextSnapshotFingerprint`
- genau eine Referenz auf den `PromptContextSnapshot`

Regeln:

- PromptRun verändert keine Domänendaten,
- Scope ist explizit,
- ein Update PromptRun referenziert genau einen PromptContextSnapshot; ein Initial PromptRun hat keinen Update Prompt Context,
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

### OpportunityGroup

Gruppe mit Type und Memberships.

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

## ResearchPromptRun

### Prompt Types

- `initial_market_research`
- `full_update`
- `company_update`
- `opportunity_update`
- `gap_filling`
- `availability_check`
- `custom_subset`

`availability_check` und andere nicht in v0.3 implementierte Prompt-Typen sind spätere Slices.

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

`PromptContextSnapshot` ist der Traceability-Pivot: ein Update PromptRun gehört genau zu einem Snapshot, ein Initial PromptRun hat keinen Update Prompt Context. Ein angewendeter Update-`ResearchImport` speichert `bundle_version = 2.0` und die validierte `prompt_context_ref`; ein initialer `1.0`-Import speichert keine Prompt Context Ref. `ResearchImport` referenziert niemals direkt einen `prompt_run_id`; mehrere Importe dürfen denselben Snapshot referenzieren.

## ExternalLink

Value Object:

- URL
- Scheme
- Display Label
- SourceId
- PostingId
- Validation Status

Regeln:

- nur `https` und optional `http`,
- keine `file:`, `javascript:`, `data:` oder proprietären Schemes,
- Öffnen nur nach expliziter Nutzeraktion,
- Linkauswahl bleibt nachvollziehbar,
- nicht erreichbare Links werden nicht automatisch gelöscht.

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

Wählt für eine Ansicht bevorzugte Posting-Links anhand dokumentierter Regeln:

1. explizit persönlich bevorzugtes Posting,
2. erreichbare Company Source,
3. jüngste erreichbare primäre Source,
4. andere erreichbare Source,
5. ansonsten kein automatisches Öffnen.

### ExternalLinkPolicy

Validiert Schemes und entscheidet, ob ein Link geöffnet werden darf.

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
- `CompanyOverviewQuery`
- `MapProjectionQuery`
- `PromptContextQuery`
- `ImportReportQuery`
- `MobileOpportunityQuery`
## Persönliche Triage

`Opportunity.tracking_status` gehört zur Vocation-Opportunity und wird ausschließlich durch persönliche Commands geändert. `PersonalAssessment` enthält Opportunity, Criterion, Wert, Begründung, Erstellzeitpunkt, Revisionsnummer und `supersedes_id`; Datensätze sind append-only, pro Opportunity/Criterion gibt es genau eine aktuelle Revision. `OpportunityDecision` enthält vorherigen und resultierenden Status, Typ, optionalen Grund und bei Restore die Referenz auf die aktive Exclusion.

Invarianten: neue und revidierte Assessments verwenden nur aktive Opportunity-Kriterien und gültige Numeric-, Categorical-, Boolean- oder Text-Werte; nur die aktuelle Revision darf revidiert werden; Create ist für ein bereits vorhandenes Opportunity/Criterion unzulässig; Exclusion benötigt einen Grund; Restore ist nur für ausgeschlossene Opportunities zulässig und löst den Default aus dem gespeicherten vorherigen Status auf; Import verändert weder PersonalAssessment noch Decision oder Tracking Status. Application Services hängen ausschließlich von Repository-Ports ab.
