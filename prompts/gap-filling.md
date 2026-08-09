# Vocation Research Update Bundle 2.0 — Gap Filling

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
This is Gap Filling. Return only requested Observation types and requested active Criteria.
Create no Company, Opportunity, or Posting. Do not emit Posting identity evidence or possible
duplicates. Context-only ancestors preserve relationships but may not be evidence targets.
Do not rewrite identity, ownership, Work Locations, or canonical fields.

## Output Schema
{{OUTPUT_SCHEMA}}
