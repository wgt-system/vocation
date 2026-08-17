# Initial Market Research Prompt

Conduct current, quality-first job-market research and return a Vocation Research Bundle 1.0.

The goal is not to fill a quota with weak matches. Prefer fewer concrete opportunities with strong current evidence over speculative or poorly evidenced results. Use the Search Profile as research strategy and the Candidate Profile, when present, only to focus discovery on plausibly suitable opportunities. Do not output or mutate personal Vocation state.

## Structured Search Profile

{{SEARCH_PROFILE}}

The Search Profile's `result_limit` is an upper bound, not a target that must be filled. Respect must-haves and must-not-haves as hard discovery constraints. Use preferred/acceptable/avoided technologies, target roles, seniority, locations, work models, employment types, industries, company characteristics and salary information to prioritize results.

Criterion policies describe what evidence matters most after import. Prioritize reliable evidence for required and higher-weight criteria, but do not invent missing facts and do not calculate or output Vocation's final personal fit/ranking.

## Candidate Profile

{{CANDIDATE_PROFILE}}

Candidate facts are private context intentionally included in this copied prompt. Use them only to improve discovery relevance. Never emit Candidate Profile data, personal Assessments, Decisions, Tracking Status, Groups/Waves, exclusions, application state or other private Vocation state in the Research Bundle.

## Research scope to echo exactly

The returned bundle must use this `research_scope` exactly, without adding fields or rewriting its values:

{{RESEARCH_SCOPE}}

## As-of date

{{AS_OF_DATE}}

Find concrete current job postings with reliable evidence. Prefer official company-career pages as primary evidence where available; use other reputable sources to discover or corroborate postings. Every stored factual claim must retain its Source Reference and observation time. Keep Company, Opportunity, Posting, Source, Source Reference, Observation, and External Assessment distinct. Mark uncertainty instead of inventing facts.

## Active Vocation assessment criteria

Use only these criterion IDs, subject types, value types, and scales or allowed values. Do not create criteria.

{{ACTIVE_ASSESSMENT_CRITERIA}}

## Complete output contract

{{OUTPUT_CONTRACT}}

Return JSON only. Do not refer to local files or add unsupported fields.