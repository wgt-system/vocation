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

Vocation-owned Supporting Subdomain für ApplicationCase-Lifecycle, private ApplicationMaterial-Metadaten und die fachliche Zuordnung privater ApplicationDocuments. ApplicationCases sind an Opportunities gebunden, aber fachlich vom Opportunity Tracking Status getrennt.

ApplicationDocument-Inhalte bleiben semantisch bei Vocation. Die implementierte Infrastruktur speichert Payloads über `ApplicationDocumentStore` außerhalb relationaler Tabellen und prüft ihre Integrität beim Schreiben und Lesen. Upload und expliziter read-only Zugriff sind implementiert; Delete/Retention, Editing/Generation, Preview/Export, Encryption und private Cross-device-Übertragung bleiben separate offene Folgesemantiken.

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

Erzeugt Vocation-owned Work-Location-bezogene Map Projections und räumliche Vergleiche. Vocation besitzt Work Location, Precision, MapLocationResolution, die Zuordnung räumlicher Features zu Opportunities sowie job-spezifische Informationen und Actions.

Generische Geospatial-Funktionen sind keine Vocation-Subdomain: Place Search/Geocoding, Map Rendering und Routing gehören systemweit zu Orientation. Vocation konsumiert die konkret benötigten Orientation-Capabilities über explizite Adapter-/Host-Grenzen und interpretiert die Ergebnisse in eigener Fachsemantik.

### External Navigation

Wählt geeignete Posting-Links aus, validiert sie und ermöglicht das explizite Öffnen im Standardbrowser.

### Data Publication

Vocation-owned Supporting Subdomain/Application Responsibility. Erzeugt versionierte, client-neutrale Published Read Projections und Publication Snapshots für externe Clients.

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

Map Rendering, Place Search/Geocoding und Routing werden nicht als eigene generische Vocation-Subdomains geführt. Ihr akzeptierter systemweiter Owner ist Orientation. Das schließt Vocation-spezifische Ports und Adapter nicht aus; diese übersetzen nur zwischen der Vocation-Anwendung und der fremden generischen Capability.

## Wichtige Abgrenzungen

- Research Prompting recherchiert nicht selbst.
- Browser Launching entscheidet nicht, welcher Link fachlich bevorzugt ist.
- Orientation entscheidet nicht über Vocation Work Location, Precision, Opportunity, Availability oder External Links.
- Vocation interpretiert generische Orientation-Ergebnisse, ohne Orientation-Provider-DTOs zu Domainobjekten zu machen.
- Schema Validation trifft keine Merge- oder Decision-Regeln.
- Datenbanktabellen bestimmen nicht das Domain Model.
- Ein neues Orientation-Feature wird nicht allein deshalb in Vocation integriert, weil Orientation es anbietet; ein konkreter Vocation-Nutzerfall muss es rechtfertigen.

## Version-1-Priorität

Muss enthalten sein:

1. Opportunity Knowledge
2. Research Prompting
3. Research Intake
4. einfache Assessments und Selection
5. Data Publication / Opportunity Overview 1.0
6. Availability/Freshness
7. Groups
8. Liste, Detail, Vergleich und Vocation-owned Map Projection
9. External Navigation
10. Application Cases, private ApplicationMaterial- und ApplicationDocument-Semantik

Bereits systemweit ausgelagert/migriert:

- generisches Map Rendering → Orientation Embed Host / `orientation.host-bridge` 1.0
- generisches Place Search/Geocoding → Orientation Place Search über `OrientationGeocoder`

Spätere Vocation-Arbeit nur nach konkreter Fachsemantik:

- automatische Verfügbarkeitsprüfung
- weitergehende Bewerbungstracking-/Bewerbungsunterlagen-Funktionen
- Document Delete/Retention, Preview/Export, Editing/Generation und Encryption
- private Cross-device-Integration
- reichhaltiger Nachfolger von Published Map Projection 1.0
- Nutzung weiterer Orientation-Capabilities wie Routing nur bei einem konkreten Vocation-Szenario
