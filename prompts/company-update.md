# Vocation Research Update Bundle 2.0 — Company Update

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
This is a Company Update. Selected Companies and their supplied Opportunities and Postings
are target subjects. Do not create Companies. New Opportunities may be created only under
an in-scope target Company. New Postings may be created under an existing in-scope target
Opportunity or under a new Opportunity created in this update under an in-scope target
Company. Do not rewrite existing canonical fields or ownership.

## Output Schema
{{OUTPUT_SCHEMA}}
