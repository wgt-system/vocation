# Vocation – Context Map

**Status:** Draft 0.2

## Kontexte

### External Research Context

Verantwortlich für Recherche, Quellenvergleich, Analyse und Erzeugung eines Research Bundle.

### Vocation Context

Besitzt Opportunities, Postings, Companies, Observations, Assessments, Decisions, Groups, ApplicationCases, private ApplicationMaterial-Metadaten, Prompt Runs, Imports und Vocation Read Models. Vocation bleibt lokale Autorität und besitzt die Publication-Adapter-Verantwortung.

### Wiiii Got This Context

Besitzt Geräte-, Plattform-, Service- und Integrationslogik.

Ein späterer Zugriff auf private ApplicationMaterial erfolgt ausschließlich über eine separate explizite private Integrationsgrenze. WGT und Conveyance besitzen keine ApplicationCase-Fachsemantik.

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
  → optional generic Relay/Storage
  → Wiiii Got This
  → Windows / iPhone
```

Muster:

- Open Host Service
- Published Read Contracts
- Customer/Supplier

Vocation entscheidet fachliche Inhalte und erzeugt die versionierte client-neutrale Published Read Projection. WGT entscheidet Geräte- und Plattformdarstellung. Relay/Storage ist Infrastruktur und kein neuer Bounded Context.

Der erste eingefrorene Vertrag ist `Opportunity Overview` Published Capability 1.0. Ein späterer lokaler Adapter kann das unveränderte Artefakt unter `/published/v1/opportunity-overview` bereitstellen; HTTP/OpenAPI und ein Relay sind nicht die Quelle der Vertragswahrheit.

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
