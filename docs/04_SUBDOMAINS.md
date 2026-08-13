# Vocation – Subdomain Classification

**Status:** Draft 0.2

## Core Subdomains

### Opportunity Knowledge

Modelliert Opportunities, Postings, Companies, Sources, Observations, Locations, Identität, Beziehungen und Historie.

### Personal Opportunity Assessment

Modelliert externe und persönliche Assessments, Risiken, Dimensionen und Bewertungsgrundlagen.

### Opportunity Selection

Modelliert Decisions, Exclusions, Prioritäten, Tracking Status, Shortlist und Wiederaufnahme.

### Application Cases

Vocation-owned Supporting Subdomain für ApplicationCase-Lifecycle und private ApplicationMaterial-Metadaten. ApplicationCases sind an Opportunities gebunden, aber fachlich vom Opportunity Tracking Status getrennt.

ApplicationDocument content bleibt semantisch bei Vocation und wird über einen `ApplicationDocumentStore` infrastrukturell gespeichert. Storage, Rendering und Verschlüsselung sind keine Domainentscheidungen dieser Slice.

## Supporting Subdomains

### Research Prompting

Erzeugt versionierte, scope-begrenzte Prompts aus Prompt Templates und Vocation Context Snapshots. Unterstützt Initial-, Update-, Teilupdate- und Gap-Filling-Recherche.

### Research Intake

Validiert und übersetzt Research Bundles über eine Anticorruption Layer.

### Availability and Freshness

Leitet vorsichtige aktuelle Einschätzungen aus zeitbezogener Evidenz ab.

### Opportunity Organization

Modelliert Groups, Application Waves und organisatorische Zusammenstellungen.

### Spatial Job-Market View

Erzeugt Work-Location-bezogene Map Projections und räumliche Vergleiche.

### External Navigation

Wählt geeignete Posting-Links aus, validiert sie und ermöglicht das explizite Öffnen im Standardbrowser.

### Data Publication

Vocation-owned Supporting Subdomain/Application Responsibility. Erzeugt versionierte, client-neutrale Published Read Projections und Publication Snapshots für externe Clients.

## Generic Subdomains

- Persistence
- File Handling
- Clipboard Handling
- JSON Schema Validation
- Search, Filtering and Sorting
- Map Rendering
- Geocoding
- Browser Launching
- Logging and Diagnostics
- Configuration
- Application Hosting

## Wichtige Abgrenzungen

- Research Prompting recherchiert nicht selbst.
- Browser Launching entscheidet nicht, welcher Link fachlich bevorzugt ist.
- Map Rendering kennt keine Opportunities.
- Schema Validation trifft keine Merge- oder Decision-Regeln.
- Datenbanktabellen bestimmen nicht das Domain Model.

## Version-1-Priorität

Muss enthalten sein:

1. Opportunity Knowledge
2. Research Prompting
3. Research Intake
4. einfache Assessments und Selection
5. Data Publication / Opportunity Overview 1.0
6. Availability/Freshness
7. Groups
8. Liste, Detail, Vergleich und Map Projection
9. External Navigation
10. Application Cases und private ApplicationMaterial-Semantik

Später:

- zentraler Map Context
- automatische Verfügbarkeitsprüfung
- weitergehende Bewerbungstracking-Domäne
- Dokument-Rendering, Verschlüsselung und externe Bewerbungseinreichung
