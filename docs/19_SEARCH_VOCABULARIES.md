# Vocation – Search Vocabularies

**Status:** implemented by #48 on the post-v0.4 `dev` line; generic geographic places remain outside this capability.

## Purpose

Structured Search Profiles need reusable terminology without turning every role, technology or industry label into hard-coded UI source code. Vocation therefore owns small local reference catalogs for terminology whose **job-search meaning** belongs to Vocation.

Current vocabulary kinds:

- `role`;
- `technology`;
- `industry`;
- `seniority`;
- `employment_type`.

Generic geographic places are intentionally excluded. Search-area place discovery belongs to the existing Orientation generic place-search boundary; Vocation owns only the job-search meaning of a selected area/radius.

## Entry semantics

A `SearchVocabularyEntry` has:

- stable local ID;
- kind;
- canonical display label;
- optional aliases used for search/discovery;
- optional stable group/category;
- active/deprecated state;
- `is_custom` marker.

Canonical labels are unique per kind after whitespace/case normalization. Aliases do not become separate identities.

## Seed catalog

Migration `0017` introduces the catalog and a conservative starter vocabulary for common software roles, technologies, industries, seniority values and employment types. The seed deliberately includes current terms such as `AI Engineer` while remaining small enough to review.

Seed data is a useful baseline, not an external truth source. Users can add a missing term immediately without waiting for a Vocation release.

## Historical Search Profile stability

Search Profile revisions continue storing their exact selected semantic values inside immutable revision snapshots. A later catalog rename/deprecation therefore does **not** rewrite an old Search Profile revision.

This is deliberate:

- catalog entries help selection and discovery;
- Search Profile revisions remain reproducible historical strategy snapshots;
- deprecation is non-destructive;
- a catalog cleanup can never silently change old research provenance.

## Internal API

Private internal endpoints:

- `GET /api/search-vocabularies` – list/search by kind, alias and active state;
- `POST /api/search-vocabularies/custom` – explicitly create a custom local entry;
- `PATCH /api/search-vocabularies/{entry_id}` – edit/deprecate/reactivate an entry;
- `POST /api/search-vocabularies/refresh-prompt` – generate a self-contained external research prompt for current role/technology/industry terminology;
- `POST /api/search-vocabularies/proposals/review` – validate returned proposal JSON and mark terms already present in the local catalog.

These are internal Vocation APIs and are not Published Vocation contracts.

## Prompt-assisted maintenance

Prompt template: `prompts/search-vocabulary-refresh.md`, version `1.0`.

The workflow is intentionally review-first:

1. Vocation snapshots the **currently active** requested role/technology/industry vocabulary into a self-contained prompt for an explicit as-of date.
2. The user copies the prompt into an external research-capable tool.
3. The external tool returns JSON contract `vocation.search-vocabulary-proposals` version `1.0` with evidence URLs.
4. Vocation validates the closed proposal structure, HTTPS evidence URLs and whether each canonical label already exists.
5. **Reviewing the result mutates no catalog state.**
6. The user explicitly chooses individual new proposals to create as local custom entries.

The proposal contract is an internal prompt workflow contract, not Research Bundle 1.0 and not a Published Vocation capability.

No paid LLM API, crawler or automatic catalog mutation is required.

## Source/evidence rules

The prompt asks external research to prefer:

- real employer career pages and established professional/job-market evidence for role terminology;
- primary project/vendor/industry evidence where practical for technology/industry terminology;
- genuinely observed market language rather than invented synonyms.

Each proposal must carry at least one absolute HTTPS evidence URL and a concise reason. Fewer justified proposals are preferred to quota filling.

## UI

Catalog administration lives under **Werkzeuge → Suchkataloge**, not in primary navigation.

The user can:

- switch vocabulary kind;
- search canonical labels and aliases;
- show/hide deprecated entries;
- add a custom term;
- deactivate/reactivate entries;
- generate the update prompt;
- paste returned proposal JSON;
- review `already known` versus new proposals;
- open evidence sources explicitly;
- accept individual new proposals.

#47 consumes these catalogs in the normal Search Profile editor so normal profile editing does not require raw newline-delimited fields.

## Ownership constraints

- Vocation owns job-search vocabulary semantics.
- Orientation owns generic place/geospatial data.
- External research proposes; Vocation/user accepts.
- Catalog lifecycle never rewrites historical Search Profile revisions.
- No new generic taxonomy microservice is introduced.
- No frozen Research or Published contract changes are implied.
