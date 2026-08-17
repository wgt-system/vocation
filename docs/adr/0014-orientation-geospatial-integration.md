# ADR-0014: Orientation geospatial integration in Vocation

**Status:** Accepted
**Date:** 2026-08-17

## Context

The System Architecture Control Plane accepts Orientation as the generic geospatial bounded context and capability owner. System ADR-0003 assigns generic spatial scenes/map rendering, place discovery/geocoding/reverse geocoding, routing and generic current-location representation to Orientation while Vocation retains job-market semantics such as Work Location, Precision, Opportunities, Availability and External Links.

Vocation previously implemented its own Nominatim geocoder and Leaflet/React Leaflet renderer. Those implementations became generic capability duplication after Orientation supplied accepted replacement boundaries.

This ADR records only **how Vocation consumes the accepted Orientation capability**. It does not redefine system-wide ownership; that remains authoritative in `wgt-system/architecture`.

## Decision

### Vocation-owned semantics remain unchanged

Vocation remains authoritative for:

- Work Location and its domain meaning;
- Work Location Precision;
- `MapLocationResolution` as Vocation supporting data;
- internal Vocation `MapProjection` and the association of spatial features with Opportunities;
- Opportunity, Company, Tracking Status, Availability and Groups/Waves information shown with a feature;
- External Link selection and validation;
- all Vocation-specific actions triggered from the map.

Orientation receives generic spatial scene data for rendering or returns generic place/geospatial results. It does not read the Vocation database or acquire Vocation business authority.

### Geocoding boundary

The Vocation application keeps a provider-neutral `Geocoder` port.

`OrientationGeocoder` is the infrastructure adapter for that port. It calls the configured Orientation backend boundary:

`GET /api/v1/places/search`

Vocation requests an explicit user-supplied query with `limit=1`, validates the bounded Orientation response and maps only the required generic values into the Vocation application-level `GeocodingResult`.

The default Orientation base URL is `http://127.0.0.1:8080` and may be overridden with `VOCATION_ORIENTATION_BASE_URL`.

Vocation does not call Photon, Nominatim or another concrete geocoding provider directly. Orientation provider references remain opaque technical references; raw provider DTOs/taxonomies do not become Vocation domain types.

If Orientation place search is unavailable or returns an invalid response, the explicit geocode action fails visibly. Vocation does not invent coordinates or silently substitute another provider. Manual location resolution and already persisted Vocation data remain usable.

### Map rendering boundary

Vocation does not implement its own generic map renderer.

`OrientationMapFrame` adapts the current Vocation-owned map read model into an Orientation Spatial Scene and communicates with the embedded Orientation map surface through the versioned `orientation.host-bridge` 1.0 contract.

The Orientation Embed Host is retained as a pinned static browser artifact under:

`frontend/public/orientation-map/`

`ORIENTATION_SOURCE_SHA.txt` records the exact Orientation source revision from which the retained artifact originated. Updating that artifact is an explicit dependency/integration update and must not silently change host-bridge semantics.

Vocation provides domain-correct feature information and opaque action references. Generic selection/rendering occurs inside Orientation; activated actions return through the host bridge and are interpreted by Vocation. Details navigation, preferred-posting selection and browser opening remain Vocation behavior.

### Published contracts remain separate

The local Orientation map composition does not mutate a Vocation Published Contract.

`Published Map Projection 1.0` remains frozen and URL-free. System architecture permits richer provider-owned spatial projections, but any richer cross-context Vocation contract requires a separately versioned successor justified by a concrete consumer scenario.

### Additional Orientation capabilities are not automatic

Orientation may provide routing, reverse geocoding, current-location representation and future generic geospatial capabilities. Their existence does not make them Vocation requirements.

Vocation integrates another Orientation capability only when a concrete Vocation user scenario requires it and the Vocation-side semantics are defined first.

## Consequences

- The former Vocation Nominatim and Leaflet/React Leaflet implementations are superseded by Orientation integration.
- Vocation keeps thin application/infrastructure adapters rather than importing Orientation domain/internal implementation classes.
- The Vocation domain and database remain independently authoritative.
- Runtime topology is not domain ownership. The embedded map artifact can be served with Vocation while place search may use a separately running Orientation backend.
- A missing Orientation runtime affects only the capability that requires it; it must produce an explicit failure rather than corrupt Vocation state.
- Packaging may later co-host or otherwise provide Orientation locally without changing this ownership boundary.
- Routing is deliberately not introduced by this ADR.

## Relationship to earlier decisions

ADR-0007 remains authoritative for the Vocation-owned Version 1 technology stack (Python/FastAPI/Pydantic, SQLAlchemy/Alembic/SQLite, React/TypeScript/Vite and the Vocation host shape).

Its original Leaflet/OpenStreetMap choice and assumption of a later unspecified map service are superseded by this ADR together with the accepted system-level Orientation ownership decision. The historical ADR is retained rather than rewritten as though that earlier choice never existed.

ADR-0005 remains authoritative for Vocation ownership of Map Projection semantics. Orientation rendering does not transfer that ownership.
