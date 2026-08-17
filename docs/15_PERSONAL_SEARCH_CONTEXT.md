# Vocation – Personal Search Context

**Status:** implemented on `feat/candidate-search-profiles`; product-acceptance work under #31/#32

## Purpose

Vocation is a quality-first personal job-market application. Job relevance therefore requires explicit knowledge of both:

1. the candidate's private qualification facts; and
2. the current job-search strategy.

These concepts are separate because facts about a person are not the same thing as a Vocation-specific search goal.

## Candidate Profile

`CandidateProfile` is private local state containing qualification facts that can inform research and later fit analysis.

The current model contains:

- headline and summary;
- education/degree facts;
- skills/technologies with an explicit familiarity level and optional note;
- languages and proficiency description;
- experience summary;
- project/portfolio highlights with technologies;
- general work-relevant interests.

Candidate Profile changes create immutable numbered revisions. The application reads the newest revision as the current profile.

Candidate Profile is not a Published Vocation Capability. It must not be exposed through Opportunity Overview, Map Projection, public examples, Research Bundle fixtures or other public surfaces.

### Extraction boundary

Candidate facts are deliberately modeled separately from Vocation job-search policy. A future shared personal-profile bounded context may own them if another concrete WGT consumer requires the same capability.

That future possibility does **not** justify another runtime service today. Until a second concrete consumer exists, Vocation persists the private facts locally behind its own application boundary.

## Search Profile

`SearchProfile` is Vocation-owned job-search strategy. Multiple named Search Profiles may coexist; one profile may be selected as the current default.

A Search Profile contains:

- name and description;
- target roles;
- target seniority;
- preferred, acceptable and avoided technologies;
- target locations;
- accepted work models (`remote`, `hybrid`, `on_site`);
- relocation willingness;
- employment-type preferences;
- preferred/avoided industries;
- preferred/avoided company characteristics;
- optional salary floor and target with currency;
- explicit must-have constraints;
- explicit must-not constraints;
- a quality-first result limit.

Search Profile changes create immutable numbered revisions. The current revision is referenced by the stable Search Profile ID.

Technology preference tiers are mutually exclusive. Salary floor may not exceed salary target. Result limit is bounded to 1–50.

## Ownership

Vocation owns:

- search intent;
- role and seniority targets;
- geographic/employment preferences;
- must-have and exclusion semantics;
- technology preference tiers;
- salary/search-result policy;
- future criterion weights, fit and ranking semantics.

Candidate facts do not own those decisions.

## Persistence

Migration `0014` introduces:

- `candidate_profile_revisions`;
- `search_profiles`;
- `search_profile_revisions`.

Revision payloads are persisted as structured JSON snapshots inside the local SQLite database. This avoids prematurely normalizing every CV/profile attribute into a separate table while still preserving exact historical search/profile states for later prompt and evaluation snapshots.

Exactly one Search Profile may be marked as default at a time.

## Internal API

Private React API:

- `GET /api/profiles/candidate`
- `PUT /api/profiles/candidate`
- `GET /api/profiles/search`
- `GET /api/profiles/search/default`
- `GET /api/profiles/search/{profile_id}`
- `POST /api/profiles/search`
- `PUT /api/profiles/search/{profile_id}`
- `POST /api/profiles/search/{profile_id}/default`
- `DELETE /api/profiles/search/{profile_id}`

These endpoints are internal Vocation API and not Published Contracts.

## Presentation

The React application exposes `Profil & Suche` with two workspaces:

- **Mein Profil** for structured private qualification facts;
- **Suchprofile** for persistent job-search strategies.

Normal users do not edit JSON. Repeating education, skill, language and project facts are managed as form rows. Search strategy list fields use ordinary multiline inputs, with one value per line where appropriate.

## Relationship to research

Research Bundle 1.0 remains frozen and compatible. The legacy Initial Research flow still accepts freeform `search_profile` and `constraints` until the profile-aware research work package replaces it as the primary workflow.

A future versioned profile-aware Research contract must reference or snapshot the exact Candidate Profile revision and Search Profile revision used for the prompt. It must not silently change Research Bundle 1.0.

## Relationship to evaluation

Weights and explainable fit do not belong to `AssessmentCriterion` definitions themselves. They are Search Profile-specific evaluation policy and are the next product-acceptance capability.

Hard must-have/must-not constraints remain distinct from weighted fit. Missing evidence must remain visible rather than silently treated as a match.
