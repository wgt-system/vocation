# Availability Check Bundle 1.0

You are checking the exact known Posting targets supplied below.

Inspect only the supplied known Posting targets. Do not discover or create replacement Opportunities or Postings, and do not substitute a similar vacancy. Return exactly one result for every selected Posting.

Use only these result values:

- `explicitly_available`
- `explicitly_unavailable`
- `temporarily_unreachable`
- `not_found`
- `indeterminate`

Distinguish transient technical failure from explicit closure. Never convert a temporary failure automatically into `explicitly_unavailable`. Use `not_found` or `indeterminate` when the exact Posting identity cannot be established reliably. Every result must include a trimmed, non-empty `evidence_summary`.

Echo the supplied `prompt_context_ref` and exact `research_scope`. Generate your own bundle-local observation IDs. Return pure JSON only, conforming exactly to Availability Check Bundle 1.0.

## Prompt Context

{{PROMPT_CONTEXT}}

## Availability Check Bundle 1.0 schema

{{OUTPUT_SCHEMA}}
