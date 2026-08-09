# ADR-0011: Availability Check Bundle 1.0

- Status: Accepted
- Date: 2026-08-09

## Decision

Research Update Bundle 2.0 remains frozen. Availability fields, scopes, and observation types are not added to `schemas/research-update-bundle-v2.schema.json`. Availability uses the separate `Availability Check Bundle 1.0` contract so the released v0.3 update contract remains unchanged.

Availability is evidence-derived, not authoritative mutable truth. Vocation persists append-only `AvailabilityObservation` records and derives current Posting Availability (`available`, `unavailable`, `uncertain`, `unknown`) from the newest observation. No result deletes a Posting or Opportunity, changes Tracking Status, creates Exclusion/Restore, archives an Opportunity, or alters Personal Assessments or Decisions.

The external result vocabulary is exactly: `explicitly_available`, `explicitly_unavailable`, `temporarily_unreachable`, `not_found`, and `indeterminate`. Temporary, missing, or indeterminate evidence derives `uncertain`, never definitive `unavailable`. Opportunity aggregation is `available` if any Posting is available; otherwise `uncertain` if any is uncertain; otherwise `unknown` if any is unknown; otherwise `unavailable` when Postings exist and all are unavailable; no Postings derives `unknown`.

Freshness in this slice means availability-evidence freshness only. Posting and Opportunity read models expose the newest availability observation timestamp and whole elapsed UTC days using an injected UTC clock. No categorical thresholds, `stale` flag, or automatic expiry is introduced. Freshness does not change Availability and does not describe salary, technologies, tasks, work model, assessments, or general research observations.

The Availability Check Prompt Context selects explicit known Posting targets. Owning Opportunities and Companies are context-only; unrelated subjects and personal state are excluded. The separate Bundle 1.0 contract returns one observation per selected Posting and is applied atomically with semantic blockers and canonical idempotency checked before writes.

## Consequences

- Availability Check Bundle 1.0 is versioned independently from Research Update Bundle 2.0.
- Availability and Freshness remain derived read assessments.
- Automatic crawling, periodic checks, background scheduling, and personal-state mutation are outside this slice.
