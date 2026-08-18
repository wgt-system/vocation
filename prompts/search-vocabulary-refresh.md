# Vocation Search Vocabulary Refresh {{PROMPT_VERSION}}

You are researching current professional job-market terminology for a private local job-search application.

As-of date: {{AS_OF_DATE}}
Vocabulary kinds in scope: {{KINDS}}

## Goal

Find genuinely useful current additions or aliases that are missing from the supplied Vocation catalog. Focus on terminology that materially improves job discovery and matching. Do not rename existing entries merely for stylistic preference and do not fill a quota.

Research current terminology using reliable recent sources. For job roles, prefer evidence from real employer career pages and established professional/job-market sources. For technologies and industries, prefer primary project/vendor/industry sources where practical. A proposed term should be recognizably used in the market, not an invented synonym.

Do not research geographic places. Places are owned by a separate geospatial capability and are outside this contract.

## Current catalog

```json
{{CURRENT_CATALOG_JSON}}
```

## Rules

- Return only terms that appear materially absent from the current catalog, including its aliases.
- `kind` must be exactly `role`, `technology`, or `industry`.
- Use a concise canonical `label` suitable for a UI selector.
- Put common equivalent spellings/names in `aliases`; do not duplicate the canonical label.
- `group` is optional and should be a concise stable category, not a source-specific taxonomy.
- `reason` must briefly explain why the term is useful/current.
- `source_urls` must contain one or more absolute HTTPS evidence URLs when a proposal is based on external evidence.
- Fewer well-supported proposals are better than speculative additions.
- Do not modify/deprecate existing entries. Vocation only uses this output as a reviewable proposal list.

## Output contract

Return JSON only, with no Markdown fences or surrounding prose:

{
  "contract": "vocation.search-vocabulary-proposals",
  "version": "1.0",
  "as_of_date": "{{AS_OF_DATE}}",
  "proposals": [
    {
      "kind": "role",
      "label": "Example Role",
      "aliases": ["Example Alternate Name"],
      "group": "Example Group",
      "reason": "Concise evidence-based reason.",
      "source_urls": ["https://example.com/evidence"]
    }
  ]
}

If no justified additions exist, return the same object with an empty `proposals` array.
