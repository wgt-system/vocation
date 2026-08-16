!element vocation {
    properties {
        "structurizr.inspection.model.softwaresystem.documentation" "info"
        "structurizr.inspection.model.softwaresystem.decisions" "info"
    }

    browserUi = container "Browser UI" "Browser-executed Vocation desktop UI for local research, triage, map, application, and document workflows." "React / TypeScript / Vite" {
        tags "Vocation Browser UI"
    }

    applicationHost = container "Local Application Host" "Local Vocation application host providing the internal presentation API, Vocation-owned publication endpoints, application/domain orchestration, and production delivery of the built frontend." "Python 3.13 / FastAPI" {
        tags "Vocation Application Host"
    }

    sqliteStore = container "SQLite Store" "Vocation-owned relational persistence for domain state, metadata, read-supporting state, and migrations." "SQLAlchemy 2 / Alembic / SQLite" {
        tags "Vocation Relational Store"
    }

    documentStore = container "Application Document Store" "Private local filesystem storage for opaque ApplicationDocument payload bytes; relational persistence stores metadata and storage references only." "Local filesystem" {
        tags "Vocation Document Store"
    }

    browserUi -> applicationHost "Loads the UI and uses the internal presentation API" "HTTP/JSON on localhost" {
        tags "Vocation Internal"
    }
    applicationHost -> sqliteStore "Reads and writes Vocation-owned relational state" "SQLAlchemy 2 / SQLite" {
        tags "Vocation Internal"
    }
    applicationHost -> documentStore "Stores and reads private ApplicationDocument payload bytes" "Local filesystem" {
        tags "Vocation Internal"
    }
}
