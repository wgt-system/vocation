# ADR-0005: Vocation besitzt die fachliche Map Projection

**Status:** Accepted

## Entscheidung

Vocation erzeugt fachlich korrekte Map Projections und besitzt Work Location, Precision sowie die persistierte MapLocationResolution. Generische geospatial capabilities werden über den separaten bounded context `wgt-system/orientation` bezogen.

Für Vocation bedeutet das:

- Place Search / Geocoding wird über die Orientation-eigene HTTP-Grenze konsumiert;
- generisches Karten-Rendering wird auf die Orientation Map Surface migriert;
- Vocation bleibt für die Übersetzung zwischen WorkLocation/MapProjection und generischen Orientation-Geodaten verantwortlich;
- Vocation publiziert weiterhin seine eigenen client-neutralen Published Capabilities.

## Konsequenzen

- Orientation besitzt keine Job-Fachlogik,
- Work Location und Precision bleiben Vocation-Verantwortung,
- Karten-Features enthalten opaque Vocation-Referenzen statt kopierter Domain Entities,
- Vocation implementiert keinen eigenen externen Geocoding-Provider mehr,
- Vocation baut keinen zweiten generischen Map-Renderer neben Orientation aus,
- ein Ausfall von Orientation degradiert nur geospatiale Vocation-Funktionen; die übrige Vocation-Anwendung bleibt eigenständig nutzbar.
