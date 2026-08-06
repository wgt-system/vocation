# Research Bundle 1.0 Output Contract

Return exactly one JSON object and no Markdown, introduction, or trailing text.

Required top-level properties, and no others:

```text
bundle_version: exactly "1.0"
bundle_id: non-empty string unique to this research run
generated_at: ISO 8601 date-time with timezone
research_scope: {type, as_of_date, search_profile, constraints}
sources: Source[]
source_references: SourceReference[]
companies: Company[]
opportunities: Opportunity[]
postings: Posting[]
observations: Observation[]
assessments: Assessment[]
warnings: string[]
```

All objects are closed: do not add properties not listed below.

```text
ResearchScope = {
  type: "initial_market_research",
  as_of_date: YYYY-MM-DD,
  search_profile: string,
  constraints: string[]
}
Source = {
  id, name,
  type: "company_careers" | "job_board" | "professional_network" | "other",
  base_url?: absolute HTTPS URL,
  notes?: string
}
SourceReference = {
  id, source_id, url: absolute HTTPS URL, observed_at: ISO date-time,
  external_reference_id?: string, display_label?: string
}
Company = {
  id, canonical_name, source_reference_id, observed_at: ISO date-time,
  alternative_names?: string[], evidence_summary?: string
}
WorkLocation = {
  label,
  precision: "exact_address" | "site" | "city" | "region" | "approximate" | "unknown",
  source_reference_id, observed_at: ISO date-time,
  city?: string, region?: string, country_code?: two uppercase letters,
  evidence_summary?: string
}
Opportunity = {
  id, company_id, canonical_title, source_reference_id,
  observed_at: ISO date-time, work_locations: WorkLocation[],
  evidence_summary?: string
}
Posting = {
  id, company_id, opportunity_id, source_reference_id, title,
  observed_at: ISO date-time,
  external_posting_id?: string, published_at?: YYYY-MM-DD,
  content_fingerprint?: string
}
Observation = {
  id,
  subject_type: "company" | "opportunity" | "posting",
  subject_id,
  type: "technology_requirement" | "task" | "seniority" |
        "experience_requirement" | "work_model" | "salary",
  value: string | number | boolean | string[],
  source_reference_id, observed_at: ISO date-time,
  confidence?: number from 0 through 1, evidence_summary?: string
}
Assessment = {
  id,
  subject_type: "company" | "opportunity" | "posting",
  subject_id, criterion_id,
  value: string | number | boolean | string[],
  origin: exactly "external_research",
  source_reference_ids: non-empty unique string[],
  created_at: ISO date-time,
  reasoning?: string
}
```

Rules:

- Bundle-local IDs must be unique within their collection and every reference must resolve.
- Do not invent Vocation internal IDs.
- Use only assessment criterion IDs explicitly supplied in the prompt and values compatible with them.
- Every stored factual claim must retain a Source Reference and observation time.
- Posting Source References must be absolute HTTPS URLs.
- Do not emit personal assessments, decisions, tracking status, exclusions, groups, or application data.
- Do not add unsupported properties. Put non-contractual caveats into `warnings` as text.
- A missing fact remains absent; do not fabricate it.
