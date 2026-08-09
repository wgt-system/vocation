# ADR-0009: Prompt Context Traceability for Update Research

- Status: Accepted
- Date: 2026-08-09

## Decision

`PromptContextSnapshot` is the traceability pivot for Update Research. An Update `ResearchPromptRun` has one nullable unique `prompt_context_ref`; Initial Research uses `null`. An applied `ResearchImport` persists `bundle_version`. An applied Update Bundle 2.0 import also persists its validated `prompt_context_ref`, while an Initial Bundle 1.0 import has no Prompt Context Ref.

`ResearchImport` stores no direct `prompt_run_id`. One snapshot belongs to at most one PromptRun, while multiple ResearchImports may reference one snapshot. Correlation References remain opaque and valid only within the snapshot that issued them.

This preserves auditability through `PromptRun → PromptContextSnapshot ← ResearchImport` without coupling import persistence directly to PromptRun persistence. Personal Assessments, Decisions and Tracking Status remain outside the public Prompt Context.
