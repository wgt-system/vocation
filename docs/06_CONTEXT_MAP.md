# Vocation – Context Map

**Status:** Draft 0.2

## Kontexte

### External Research Context

Verantwortlich für Recherche, Quellenvergleich, Analyse und Erzeugung eines Research Bundle.

### Vocation Context

Besitzt Opportunities, Postings, Companies, Observations, Assessments, Decisions, Groups, ApplicationCases, private ApplicationMaterial-Metadaten, private ApplicationDocuments, Prompt Runs, Imports und Vocation Read Models. Vocation bleibt lokale Autorität und besitzt die Publication-Adapter-Verantwortung.

### Wiiii Got This Context

Besitzt Geräte-, Plattform-, Service- und Integrationslogik.

Ein späterer Zugriff auf private ApplicationMaterial erfolgt ausschließlich über eine separate explizite private Integrationsgrenze. WGT und Conveyance besitzen keine ApplicationCase-Fachsemantik.

Private ApplicationDocument-Payloads bleiben außerhalb des Context Maps für Published Contracts; ein späterer privater Transport darf nur opaque protected payloads relayen.

### Conveyance Context

Besitzt generische langlebige Zustellung und Relay-Semantik, opaque Channels und Envelopes sowie die dafür akzeptierten technischen Trust- und Security-Mechanismen.

Conveyance versteht keine Vocation-Fachsemantik und ist keine Autorität für Vocation-Daten.

### Illumination Context

Besitzt Fragen, Lösungen, Übungen und Lernfortschritt.

### Orientation Context

Besitzt die systemweit akzeptierte generische Geospatial-Capability: Spatial Scenes und Map Rendering, Place Search/Geocoding/Reverse Geocoding, Routing sowie generische Current-Location-Repräsentation.

Orientation besitzt keine Vocation-Fachsemantik und keine autoritativen Vocation-Daten. Insbesondere bleiben Work Location, Precision, Opportunity, Company, Posting, External Links, Availability und Vocation Map Projection im Vocation Context.

## Research → Vocation

Muster:

- Upstream/Downstream
- Published Language: Research Bundle
- Anticorruption Layer
- Customer/Supplier

Vocation definiert die für einen belastbaren Import benötigten Felder. Research kann zusätzliche Informationen liefern, aber nicht Vocation-interne Decisions verändern.

## Vocation → Research

Vocation veröffentlicht keinen Domain-Schreibzugriff. Es erzeugt stattdessen Research Prompts und Prompt Context Snapshots. Diese sind eine kontrollierte, read-only Übergabe an den Research Context.

Muster:

- Published Language: Research Prompt Package
- Customer/Supplier
- keine gemeinsame Domain Entity

## Vocation → Wiiii Got This

```text
Vocation
  → Vocation Publication Adapter
  → Wiiii Got This Windows
  → Conveyance (opaque protected delivery)
  → Wiiii Got This iPhone
```

## Vocation ↔ Illumination

Version 1: `Separate Ways`.

Später optional: Published Language für Learning References.

## Vocation → Orientation

Vocation konsumiert Orientation nur für generische geospatial Ergebnisse und Darstellung und interpretiert diese anschließend in eigener Fachsemantik.

Aktuell implementiert:

- explizite Work-Location-Geocodierung über den Vocation `Geocoder`-Port und den `OrientationGeocoder`-Adapter gegen Orientation Place Search;
- generisches Kartenrendering über den eingebetteten Orientation Embed Host und `orientation.host-bridge` 1.0;
- Vocation adaptiert seine interne Map Projection in eine Orientation Spatial Scene;
- Orientation-Actions werden zurück an Vocation vermittelt; Vocation entscheidet über Opportunity-Details und External-Link-Aktionen.

Vocation bleibt für Work Location und Precision autoritativ. Orientation erzeugt oder verändert keine Opportunities, MapLocationResolutions, Tracking-Zustände oder External Links.

## Externe Provider

- Place-/Geocoding-Provider: Orientation-Infrastruktur hinter Orientation-owned Ports; Vocation ruft keinen konkreten Provider direkt auf.
- Map Style/Tiles: Orientation-Infrastruktur bzw. Map-Surface-Providerintegration.
- Browser/Operating System: technischer Vocation-Adapter für explizite externe Navigation.

## Verbotene Kopplungen

- direkter Datenbankzugriff zwischen Kontexten,
- gemeinsame Domain Entities,
- gemeinsame Fachlogikbibliotheken,
- WGT liest nie die Vocation-Datenbank und importiert keine Vocation-Domainklassen,
- WGT modelliert keine Vocation-Business-Semantik,
- Orientation liest keine Vocation-Tabellen und interpretiert keine Vocation-Business-Semantik,
- Vocation implementiert keinen konkurrierenden generischen Map-/Geocoding-/Routing-Stack, wenn die akzeptierte Orientation-Capability den konkreten Bedarf abdeckt,
- Research Bundle wird direkt persistiert als Domain Model.

Die systemweite Ownership und Cross-Context-Policy werden durch `wgt-system/architecture` festgelegt; dieses Dokument konkretisiert nur die Vocation-Seite dieser Beziehungen.
