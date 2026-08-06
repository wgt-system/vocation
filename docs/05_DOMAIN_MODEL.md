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
- optionale Referenz auf späteren Import

Regeln:

- PromptRun verändert keine Domänendaten,
- Scope ist explizit,
- eingebetteter Kontext ist read-only,
- Ausgabeanforderung verweist auf eine Bundle Version.

### OpportunityAssessment

Historische Bewertung mit Origin, Type, Dimensions, Result und Reasoning.

### OpportunityDecision

Bewusste persönliche Entscheidung mit Reason und möglicher Reversal-Beziehung.

### OpportunityGroup

Gruppe mit Type und Memberships.

### DuplicateCase

Mögliche oder bestätigte Identitätsbeziehung.

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

### Prompt Scope

Enthält:

- Scope Type
- referenzierte Vocation IDs
- gewünschte Felder oder Fragen
- erlaubten Änderungsbereich
- Stichtag
- erwartete Bundle Version

### Invarianten

1. Ein Update-Prompt muss bekannte IDs und den Scope enthalten.
2. Ein Prompt darf nicht behaupten, selbst recherchiert zu haben.
3. Ein Prompt muss die gewünschte Ausgabe als reines JSON verlangen.
4. Ein Teilupdate darf keine außerhalb des Scopes liegenden Änderungen als verbindlich ausgeben.
5. Persönliche Decisions und Assessments werden als geschützt markiert.

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
