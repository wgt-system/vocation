# Vocation Research Update Bundle 2.0 — Opportunity Update

Return JSON only. Generate a Bundle with bundle_version exactly "2.0".
Echo prompt_context_ref and research_scope exactly as supplied below.
Use only the supplied opaque correlation refs. Generate your own unique bundle-local IDs.
Never emit internal Vocation IDs. Do not emit or change personal state, Tracking Status,
Personal Assessments, Decisions, Exclusions, Restore history, Groups, or Waves.
Do not derive Availability or Freshness. Do not automatically merge or resolve duplicates.

## Prompt Context
{{PROMPT_CONTEXT}}

## Active Assessment Criteria
{{ACTIVE_ASSESSMENT_CRITERIA}}

## Scope restrictions
This is an Opportunity Update. Selected Opportunities and their supplied Postings are targets.
Owning Companies are context only. Do not create Companies or Opportunities. New Postings may
be created only under a selected target Opportunity. Do not implement direct Posting selection
and do not rewrite existing canonical fields or ownership.

## Output Schema
{{OUTPUT_SCHEMA}}
