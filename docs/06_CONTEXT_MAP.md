# Vocation – Context Map

**Status:** current Vocation-side context relationships; system-wide ownership remains authoritative in `wgt-system/architecture`.

## Kontexte

### External Research Context

Verantwortlich für externe Recherche, Quellenvergleich und Erzeugung der jeweils angeforderten versionierten Research-/Update-/Availability-Ausgabe.

External Research ist keine Autorität für private Vocation-Zustände. Es kann Evidenz/Vorschläge liefern, aber keine Personal Assessments, Decisions, Tracking Status, Notes, Candidate/Search Profiles oder ApplicationCases mutieren.

### Vocation Context

Besitzt Opportunities, Postings, Companies, Observations, Assessments, Decisions, Candidate/Search Profiles, Evaluation Policy/Fit, Groups, ApplicationCases, private ApplicationMaterial-/ApplicationDocument-Semantik, Prompt Contexts/Runs, Imports, Availability und Vocation Read Models.

Vocation bleibt lokale Autorität und besitzt seine Publication-Adapter-Verantwortung.

### Wiiii Got This Context

Besitzt system-/produktübergreifende Integrations- und Consumer-Semantik, nicht die Vocation-Domain.

Ein späterer Zugriff auf private Vocation-Application-/Profile-Daten erfolgt ausschließlich über eine separate explizite private Integrationsgrenze. WGT und Conveyance besitzen keine ApplicationCase-, Search-Profile- oder Opportunity-Fachsemantik.

### Conveyance Context

Besitzt generische langlebige Zustellung/Relay-Semantik, opaque Channels/Envelopes und akzeptierte technische Trust-/Security-Mechanismen.

Conveyance versteht keine Vocation-Fachsemantik und ist keine Autorität für Vocation-Daten.

### Illumination Context

Besitzt Fragen, Lösungen, Übungen und Lernfortschritt. Aktuell `Separate Ways` zu Vocation, solange kein konkreter versionierter Learning-Reference-Use-Case vereinbart ist.

### Orientation Context

Besitzt die systemweit akzeptierte generische Geospatial-/Place-Capability: Spatial Scenes/Map Rendering, Place Search/Geocoding/Reverse Geocoding, Routing und generische Current-Location-Repräsentation.

Orientation besitzt keine Vocation-Fachsemantik und keine autoritativen Vocation-Daten. Insbesondere bleiben Work Location, Search Area, Radius-/Relocation-/Remote-Policy, Precision, Opportunity, Company, Posting, External Links, Availability und Vocation Map Projection im Vocation Context.

## External Research → Vocation

Muster:

- Upstream/Downstream;
- versionierte Published Language/Contract Bundles;
- Anticorruption-/Validation-/Scope-/Identity-Grenze;
- Vocation als Consumer mit eigenen Invarianten.

Research kann zusätzliche Evidenz liefern, aber nicht Vocation-interne persönliche/private Zustände verändern.

## Vocation → External Research

Vocation veröffentlicht keinen Domain-Schreibzugriff. Es erzeugt Research Prompts und immutable Prompt Context Snapshots als kontrollierte read-only Übergabe.

Profile-aware Initial Research kann nach expliziter Nutzerwahl einen Candidate-Profile-Snapshot und immer die exakte Search-Profile-Revision enthalten. Update-Prompts verwenden scope-lokale opaque Correlation References.

Muster:

- versioniertes Prompt Package;
- explizite Disclosure;
- keine gemeinsame Domain Entity;
- returned output muss wieder durch Vocation Intake.

## Vocation → Wiiii Got This / Conveyance

Vocation stellt nur explizit versionierte Published/protected Capabilities bereit. WGT liest nie direkt die Vocation-Datenbank. Conveyance kann später opaque geschützte Payloads transportieren, ohne Vocation-Fachobjekte zu interpretieren.

Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben provider-owned frozen contracts.

## Vocation → Orientation

Vocation konsumiert Orientation für generische geospatial Ergebnisse/Darstellung und interpretiert diese anschließend in eigener Fachsemantik.

Aktuell implementiert:

- explizite Work-Location-Geocodierung über Vocation `Geocoder` → `OrientationGeocoder` → Orientation Place Search;
- generisches Kartenrendering über den eingebetteten Orientation Embed Host und `orientation.host-bridge` 1.0;
- Vocation adaptiert seine interne Map Projection in eine Orientation Spatial Scene;
- Orientation-Actions werden zurück an Vocation vermittelt; Vocation entscheidet über Opportunity-Details und External-Link-Aktionen.

Geplant in #47:

- Search Profile Search Areas wählen generische Orte ebenfalls über eine Orientation-backed Place-Search-Grenze;
- Vocation persistiert/interpretierst die job-spezifische Search-Area-/Radius-Politik, nicht generische Geocoder-Providersemantik.

Orientation erzeugt oder verändert keine Opportunities, Search Profiles, MapLocationResolutions, Tracking-Zustände oder External Links.

## Future Document Extraction

Die geplante CV-/Zeugnis-Extraktion aus #46 erzeugt **aktuell keinen neuen Context/Microservice**.

Erste Grenze:

```text
Vocation Candidate/Profile Use Case
  → provider-neutraler Document Extraction Port
  → lokaler/ersetzbarer Parser-OCR-Adapter
```

Der Adapter kann Text/Layout/OCR-Ergebnisse liefern. Vocation interpretiert sie als reviewbare `DocumentExtractionProposal` und bleibt autoritativ für Candidate-Profile-/Application-Semantik.

Ein separater systemweiter Document-Understanding-Context/Service wird nur eingeführt, wenn:

- mindestens ein weiterer konkreter Bounded Context dieselbe generische Capability benötigt, oder
- Runtime-, Security-, Deployment- oder Dependency-Eigenschaften eine eigenständige Servicegrenze materiell rechtfertigen.

Die Existenz von PDF/OCR-Bibliotheken allein rechtfertigt keine Microservice-Grenze.

## Externe Provider

- Place-/Geocoding-Provider: Orientation-Infrastruktur hinter Orientation-owned Ports; Vocation ruft keinen konkreten Provider direkt auf.
- Map Style/Tiles: Orientation-Infrastruktur bzw. Map-Surface-Providerintegration.
- Browser/Operating System: technischer Vocation-Adapter für explizite externe Navigation.
- künftige PDF-/OCR-Libraries: zunächst Infrastruktur hinter einem Vocation-owned Extraction-Port, keine externe Fachautorität.

## Verbotene Kopplungen

- direkter Datenbankzugriff zwischen Kontexten;
- gemeinsame Domain Entities als Integrationsvertrag;
- WGT liest Vocation-Tabellen oder importiert Vocation-Domainklassen;
- Orientation interpretiert Vocation-Business-Semantik;
- Vocation implementiert einen konkurrierenden generischen Place-/Map-/Routing-Stack, wenn Orientation den konkreten Bedarf abdeckt;
- Research Bundle wird direkt als Domain Model persistiert;
- externe Research-/Extraction-/Generation-Ausgabe überschreibt private Vocation-Fakten ohne expliziten Vocation-Use-Case;
- ein neuer Service wird nur zur Codeorganisation oder wegen einer einzelnen Library eingeführt.

Die systemweite Ownership und Cross-Context-Policy werden durch `wgt-system/architecture` festgelegt; dieses Dokument konkretisiert ausschließlich die Vocation-Seite dieser Beziehungen.
