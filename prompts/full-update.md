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

This is a Full Update. Existing Companies, Opportunities, and Postings are in scope targets.
New Companies, Opportunities, and Postings are allowed. Preserve Company and Opportunity
ownership relationships and provide Source References for every external fact.

## Output Schema

{{OUTPUT_SCHEMA}}
