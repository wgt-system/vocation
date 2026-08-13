# ADR-0013: Private ApplicationDocument content and storage boundary

**Status:** Accepted
**Date:** 2026-08-13

## Decision

Vocation owns the semantic document content attached to an `ApplicationMaterial` revision. `ApplicationDocument` is private Vocation-owned content associated with exactly one immutable material revision. Each revision may have zero or one document; a revision without content remains valid.

The V1 semantic representation is an opaque local binary payload plus minimal metadata: stable `document_id`, `material_id`, `material_revision`, original display filename, media type, byte size, SHA-256 content digest, and `created_at`. Allowed media types are `application/pdf`, `text/plain`, and `text/markdown`. Payload bytes are immutable once attached. Replacing content requires a new material revision; one document cannot belong to multiple revisions. Filename is presentation metadata; SHA-256 is integrity/deduplication metadata, not domain identity.

## Storage and privacy boundary

An `ApplicationDocumentStore` infrastructure port separates semantic ownership from physical storage. Domain/application code knows neither filesystem paths, OS directories, SQLite blob layout, cloud locations, nor Conveyance transport. The store uses opaque Vocation-owned storage references. A future local implementation may keep bytes outside relational domain tables and store metadata plus an opaque reference in the database; no exact path is frozen.

Actual bytes are private. Stored byte size and SHA-256 must match the payload; missing bytes for persisted metadata are explicit integrity errors. Equal digests do not imply shared ownership or deletion, and automatic deduplication is not decided. Document content and metadata never appear in Published Contracts, Research/Availability Bundles, Prompt Context Snapshots, public fixtures, logs, or publication endpoints. ApplicationCase lifecycle does not create, replace, render, submit, or delete documents.

PDF generation, text editing, LaTeX, templates, generation, preview, file-picker/import UX, export/download, encryption, retention, backup, WGT/private access, Conveyance payloads, synchronization, and submission automation remain open.
