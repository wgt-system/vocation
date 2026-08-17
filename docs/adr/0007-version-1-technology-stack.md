# ADR-0007: Technologie-Stack für Version 1

**Status:** Accepted; geospatial portion superseded by ADR-0014

## Kontext

Vocation benötigt einen eigenständig startbaren lokalen Dienst mit Desktop-orientierter Weboberfläche, eigener Datenhaltung und versionierten Verträgen. Zum Zeitpunkt dieser Entscheidung sollte keine Laufzeitabhängigkeit zu Wiiii Got This, Illumination oder einem damals noch nicht bestimmten späteren Map Service entstehen.

Die spätere systemweite Architekturentscheidung hat Orientation als akzeptierten generischen Geospatial-Bounded-Context eingeführt. Die daraus folgende Vocation-Integrationsform ist in ADR-0014 dokumentiert. Diese spätere Entscheidung ändert nicht den Vocation-owned Kern dieses Technologie-Stacks.

## Entscheidung

Version 1 verwendet:

- Python 3.13
- FastAPI und Pydantic
- SQLAlchemy 2, Alembic und SQLite
- `jsonschema` für den Research-Bundle-Vertrag
- pytest
- React, TypeScript und Vite
- Vitest und React Testing Library
- ursprünglich Leaflet und OpenStreetMap für den späteren Karten-Slice

Die Python-Anwendung startet den lokalen HTTP-Dienst. Im Produktionsmodus liefert FastAPI das gebaute Frontend aus und kann nach erfolgreichem Start die lokale Vocation-URL über den Standardbrowser öffnen. Die Struktur bleibt für eine spätere PyInstaller-Distribution geeignet.

## Supersession der Geospatial-Entscheidung

Die ursprüngliche Leaflet/OpenStreetMap-Auswahl und die Annahme eines späteren unbestimmten Map Service sind nicht mehr die aktuelle Vocation-Architektur.

ADR-0014 supersediert ausschließlich diesen generischen Geospatial-Teil:

- generisches Map Rendering wird über den Orientation Embed Host und `orientation.host-bridge` 1.0 konsumiert;
- generisches Place Search/Geocoding wird über `OrientationGeocoder` gegen die Orientation-Anwendungsgrenze konsumiert;
- Vocation behält Work Location, Precision, MapLocationResolution, Map Projection und Job-Market-Actions;
- weitere Orientation-Capabilities werden nur bei konkretem Vocation-Nutzerfall integriert.

Die ursprüngliche Entscheidung bleibt hier als historische Architekturentscheidung sichtbar und wird nicht rückwirkend umgeschrieben.

## Konsequenzen

- Vocation ist ohne Wiiii Got This oder Illumination fachlich autoritativ und lokal nutzbar; akzeptierte generische System-Capabilities dürfen über explizite Grenzen konsumiert werden.
- Frontend und Backend werden in der Produktion gemeinsam gestartet.
- Die SQLite-Struktur wird mit Alembic migriert.
- Domain-Logik bleibt frei von FastAPI- und SQLAlchemy-Abhängigkeiten.
- Das Frontend verwendet die lokalen Vocation-Grenzen; generische Orientation-Integration bleibt hinter expliziten Adapter-/Host-Grenzen.
- Docker, Cloud-Infrastruktur, Authentifizierung und Multi-User-Betrieb werden durch diese Entscheidung nicht eingeführt.
- Die automatische Browseröffnung darf nur die lokale Vocation-Oberfläche betreffen; externe Posting-URLs benötigen weiterhin eine explizite Nutzeraktion.
- Die konkrete Deployment-/Packaging-Topologie für Orientation ist von Vocation-Domainownership getrennt.
