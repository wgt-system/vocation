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

### möglicher Shared Map Context

Kann später serviceübergreifende Map Contributions rendern und kombinieren.

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

## Vocation → Shared Map Context

Später optional:

- Published Language: Map Contribution
- Customer/Supplier

Vocation besitzt Work Location und Map Projection. Ein Map Context besitzt Rendering und serviceübergreifende Komposition.

## Externe Provider

- Geocoder: Anticorruption Layer
- Map Tiles: technische Infrastruktur
- Browser/Operating System: technischer Adapter

## Verbotene Kopplungen

- direkter Datenbankzugriff zwischen Kontexten,
- gemeinsame Domain Entities,
- gemeinsame Fachlogikbibliotheken,
- WGT liest nie die Vocation-Datenbank und importiert keine Vocation-Domainklassen,
- WGT modelliert keine Vocation-Business-Semantik,
- Map Context liest Vocation-Tabellen,
- Research Bundle wird direkt persistiert als Domain Model.
