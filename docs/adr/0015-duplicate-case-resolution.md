# ADR-0015: Duplicate Case resolution without merge

**Status:** Accepted
**Date:** 2026-08-17

## Context

Vocation already creates `DuplicateCase` records when Research Update evidence indicates that two existing Opportunities or two existing Postings may represent the same underlying subject but deterministic identity is insufficient. The current model deliberately keeps those cases unresolved and never merges or rewrites subjects automatically.

The unresolved queue now needs an explicit user review workflow. A review decision must be auditable and correctable without turning the first resolution feature into an irreversible identity-merge subsystem.

## Decision

### DuplicateCase remains evidence

`DuplicateCase` continues to represent the stable canonical pair and the evidence that caused the possible-duplicate case to exist. Existing evidence fields are not overwritten by a review decision.

A later Research import that encounters the same canonical pair reuses the existing DuplicateCase. It must not clear, replace, reopen or otherwise change a user's Duplicate Decisions.

### DuplicateDecision is append-only

Vocation introduces an immutable `DuplicateDecision` belonging to exactly one DuplicateCase.

Each decision contains:

- stable `decision_id`;
- `duplicate_case_id`;
- monotonically increasing `sequence` within the case;
- one outcome;
- a nonblank user-provided reason;
- `decided_at`.

Allowed outcomes are exactly:

- `confirmed_duplicate`;
- `confirmed_distinct`;
- `related_but_distinct`;
- `keep_unresolved`.

Decisions are append-only. Existing decisions are never edited or deleted.

### Current review state

The latest decision by sequence is the current user judgment.

A case with no decision is **unreviewed and unresolved**.

A latest decision of `keep_unresolved` means **reviewed but unresolved**.

A latest decision of `confirmed_duplicate`, `confirmed_distinct` or `related_but_distinct` means **resolved for review purposes**.

The user may correct a previous judgment by appending a different outcome. The complete history remains visible. Repeating the same outcome as the current decision is a no-op/conflict and does not create another history entry.

### Explicit user action only

A DuplicateDecision is created only by an explicit user action in Vocation.

Research imports, Availability imports, prompt generation, Groups/Waves, ApplicationCase lifecycle changes, Orientation integration and Published Contracts may neither create nor modify Duplicate Decisions.

### No merge in Slice 18

`confirmed_duplicate` is a classification only. Slice 18 does **not**:

- merge Opportunities or Postings;
- choose a canonical surviving subject;
- delete either subject;
- create aliases;
- re-parent Postings;
- move Work Locations;
- combine Observations or Assessments;
- transfer Tracking Status or Decisions;
- move Group/Wave memberships;
- move ApplicationCases, ApplicationMaterials or ApplicationDocuments;
- rewrite Source References or import history;
- change Published Contract identity.

Any future merge capability requires its own explicitly frozen semantics for authority, surviving identity, reference rewriting, history retention and conflict handling. A `confirmed_duplicate` decision may later be a precondition for such a capability, but does not itself perform it.

### Review read model

The review UI may use derived subject summaries and Source Reference summaries to make the decision understandable. These are read-model data only and create no new domain ownership.

For Opportunity subjects a useful summary includes the Opportunity title and Company. For Posting subjects it includes the Posting title and Source. Duplicate evidence Source References may be displayed as internal review context.

### Privacy and publication

DuplicateCases and DuplicateDecisions remain internal Vocation state. They are not added to Published Opportunity Overview 1.0, Published Map Projection 1.0, Research Bundle contracts, Availability Bundle contracts or Prompt Context Snapshots.

## Consequences

- The unresolved duplicate queue can be reviewed without irreversible identity mutation.
- Review history remains auditable and corrections do not erase prior judgments.
- Existing import idempotency and pair canonicalization remain unchanged.
- A later merge slice stays intentionally separate and must handle every affected aggregate/reference explicitly.
- No system-wide ADR is required because this decision changes only Vocation-owned domain semantics and internal persistence/UI behavior.
