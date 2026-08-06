# ADR-0007: Technologie-Stack für Version 1

**Status:** Accepted

## Kontext

Vocation benötigt einen eigenständig startbaren lokalen Dienst mit Desktop-orientierter Weboberfläche, eigener Datenhaltung und versionierten Verträgen. Es darf keine Laufzeitabhängigkeit zu Wiiii Got This, Illumination oder einem späteren Map Service entstehen.

## Entscheidung

Version 1 verwendet:

- Python 3.13
- FastAPI und Pydantic
- SQLAlchemy 2, Alembic und SQLite
- `jsonschema` für den Research-Bundle-Vertrag
- pytest
- React, TypeScript und Vite
- Vitest und React Testing Library
- Leaflet und OpenStreetMap erst im späteren Karten-Slice

Die Python-Anwendung startet den lokalen HTTP-Dienst. Im Produktionsmodus liefert FastAPI das gebaute Frontend aus und kann nach erfolgreichem Start die lokale Vocation-URL über den Standardbrowser öffnen. Die Struktur bleibt für eine spätere PyInstaller-Distribution geeignet.

## Konsequenzen

- Vocation ist ohne andere fachliche Projekte startbar.
- Frontend und Backend werden in der Produktion gemeinsam gestartet.
- Die SQLite-Struktur wird mit Alembic migriert.
- Domain-Logik bleibt frei von FastAPI- und SQLAlchemy-Abhängigkeiten.
- Das Frontend verwendet ausschließlich die veröffentlichte lokale API.
- Docker, Cloud-Infrastruktur, Authentifizierung und Multi-User-Betrieb werden nicht eingeführt.
- Die automatische Browseröffnung darf nur die lokale Vocation-Oberfläche betreffen; externe Posting-URLs benötigen weiterhin eine explizite Nutzeraktion.
