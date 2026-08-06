# ADR-0005: Vocation besitzt die fachliche Map Projection

**Status:** Accepted

## Entscheidung

Vocation erzeugt fachlich korrekte Map Projections. Das Rendering kann lokal oder später durch einen Shared Map Context erfolgen.

## Konsequenzen

- Renderer besitzt keine Job-Fachlogik,
- Work Location und Precision bleiben Vocation-Verantwortung,
- Karten-Pins enthalten Referenzen, keine kopierten Domain Entities.
