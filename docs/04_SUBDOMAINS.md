# Vocation – Subdomain Classification

**Status:** current through the implemented post-v0.4 personal-search baseline; planned post-acceptance work is marked.

## Core Subdomains

### Opportunity Knowledge

Modelliert Opportunities, Postings, Companies, Sources, Observations, Work Locations, Identität, Beziehungen und Historie.

### Personal Search Strategy and Fit

Vocation-owned Core-Semantik für:

- mehrere revisionierte Search Profiles;
- Zielrollen, Seniority, Technologien, Branchen, Arbeitsmodelle, Beschäftigungsarten und Search-Area-Politik;
- harte Must-/Must-not-Constraints;
- Search-Profile-spezifische Evaluation Policy;
- deterministischen erklärbaren Opportunity Fit und Evidence Completeness;
- künftig Research-Strategy-/Coverage-Semantik (#49).

Candidate-Profile-Personenfakten sind davon bewusst getrennt. Sie bleiben aktuell lokal in Vocation, damit Search/Research/Fit nutzbar sind, ohne Person-Fakten und Suchpolitik fachlich zu vermischen.

### Personal Opportunity Assessment and Selection

Modelliert:

- External und Personal Assessments;
- persönliche Decisions;
- Exclusion/Restore;
- Tracking Status;
- private Opportunity Notes;
- persönliche Auswahl-/Priorisierungssicht.

Importierte Research-Evidenz darf diesen Zustand nicht still überschreiben.

### Application Cases

Vocation-owned Subdomain für ApplicationCase-Lifecycle, private ApplicationMaterial-Revisionen und die fachliche Zuordnung privater ApplicationDocuments. ApplicationCases sind an Opportunities gebunden, aber fachlich vom Opportunity Tracking Status getrennt.

ApplicationDocument-Inhalte bleiben semantisch bei Vocation. Die implementierte Infrastruktur speichert Payloads über `ApplicationDocumentStore` außerhalb relationaler Tabellen und prüft ihre Integrität beim Schreiben und Lesen. Upload und expliziter read-only Zugriff sind implementiert.

#50 erweitert die Produktrichtung um einen verständlichen Bewerbungsworkspace und explizit reviewbare prompt-assistierte Application Drafts; automatische Submission bleibt ausgeschlossen.

## Supporting Subdomains

### Candidate Profile

Private lokale, revisionierte Person-/Qualifikationsfakten für Research, Fit-Kontext und künftig Bewerbungsarbeit.

Aktuell ist diese Capability Bestandteil von Vocation, aber bewusst von Vocation-spezifischer Search Policy getrennt. Eine spätere Extraktion in einen gemeinsamen Personal-Profile-Kontext wird erst durch einen zweiten konkreten Consumer gerechtfertigt.

#46 plant reichhaltigere strukturierte Career Facts und wiederverwendbare CV-/Nachweis-Dokumente.

### Research Prompting

Erzeugt versionierte, scope-begrenzte Prompts aus Prompt Templates und Vocation Context Snapshots.

Implementiert sind profile-aware Initial Research, Full/Company/Opportunity Update, Gap Filling und Availability Check. Prompting recherchiert nicht selbst.

#49 plant mehrere explizite Research Strategies/Runs, ohne aus Prompting einen automatischen Crawler zu machen.

### Research Intake

Validiert und übersetzt versionierte Research-/Update-Bundles über kontrollierte Anticorruption-/Scope-/Identity-Grenzen und wendet sie atomar an.

### Availability and Freshness

Speichert append-only Availability Observations und leitet daraus vorsichtige aktuelle Posting-/Opportunity-Availability sowie Alter der Availability-Evidenz ab.

Posting-Alter oder ein alter Suchmaschinen-Treffer ist nicht automatisch `unavailable`; aktuelle Aktionabilität wird über passende Evidenz geprüft.

### Opportunity Organization

Modelliert `OpportunityGroup`, `ApplicationWave` und geordnete Memberships.

Dies ist Domain-Semantik, nicht zwangsläufig finaler UI-Wortlaut. Die manuelle Produktabnahme hat literal `Groups/Waves`/`Organisation` als Hauptnavigation nicht akzeptiert; #45/#50 bearbeiten die Präsentation.

### Spatial Job-Market View

Erzeugt Vocation-owned Work-Location-bezogene Map Projections und räumliche Vergleiche. Vocation besitzt Work Location, Precision, MapLocationResolution, die Zuordnung räumlicher Features zu Opportunities sowie job-spezifische Informationen und Actions.

Generische Geospatial-Funktionen sind keine Vocation-Subdomain: Place Search/Geocoding, Map Rendering und Routing gehören systemweit zu Orientation. Vocation konsumiert benötigte Orientation-Capabilities über explizite Adapter-/Host-Grenzen und interpretiert die Ergebnisse in eigener Fachsemantik.

Künftige Search Areas aus #47 folgen derselben Ownership-Regel: generischer Ort via Orientation, job-spezifische Search-Area-/Radius-/Remote-/Relocation-Semantik in Vocation.

### External Navigation

Wählt geeignete Posting-Links aus, validiert sie und ermöglicht das explizite Öffnen im Standardbrowser.

### Data Publication

Vocation-owned Supporting Subdomain/Application Responsibility. Erzeugt versionierte, client-neutrale Published Read Projections für externe Consumer. Publication überträgt keine fachliche Autorität.

## Generic/technical concerns inside Vocation

- Persistence
- File Handling
- Clipboard Handling
- JSON Schema Validation
- Search, Filtering and Sorting
- Browser Launching
- Logging and Diagnostics
- Configuration
- Application Hosting
- Adapter/Host integration with accepted system capabilities

Map Rendering, Place Search/Geocoding und Routing werden nicht als eigene generische Vocation-Subdomains geführt. Ihr akzeptierter systemweiter Owner ist Orientation.

### Document extraction – noch keine eigene Subdomain/Microservice

PDF-Text-/Layout-/OCR-Extraktion ist derzeit **keine** separate Vocation- oder WGT-Servicegrenze.

Wenn #46 Extraction einführt, beginnt sie als austauschbarer technischer Port/Adapter. Vocation besitzt die Interpretation als Candidate-Profile-/Application-Semantik. Ein generischer Document-Understanding-Service wird erst eingerichtet, wenn ein zweiter konkreter Consumer oder eigenständige Runtime-/Security-/Dependency-Anforderungen die Grenze rechtfertigen.

## Wichtige Abgrenzungen

- Research Prompting recherchiert nicht selbst.
- External Research darf private Vocation-Entscheidungen/Profiles/Application-State nicht still mutieren.
- Browser Launching entscheidet nicht, welcher Link fachlich bevorzugt ist.
- Orientation entscheidet nicht über Search Areas, Work Locations, Opportunity, Fit, Availability oder External Links.
- Vocation interpretiert generische Orientation-Ergebnisse, ohne Orientation-Provider-DTOs zu Domainobjekten zu machen.
- Schema Validation trifft keine Merge- oder Decision-Regeln.
- Datenbanktabellen bestimmen nicht das Domain Model.
- Candidate Profile ist keine Search Strategy.
- ApplicationCase ist nicht Opportunity Tracking Status.
- OpportunityGroup/ApplicationWave-Domainbegriffe müssen nicht literal in der UI erscheinen.
- Ein neues Orientation-Feature wird nur bei einem konkreten Vocation-Nutzerfall integriert.
- Ein neuer Microservice wird nicht allein deshalb erzeugt, weil eine Bibliothek/Dateiart technisch separat behandelbar wäre.
