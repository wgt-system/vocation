# Vocation – Prompt Workflows

**Status:** Initial/Update/Gap/Availability prompt workflows implemented; manual real-market strategy expansion tracked by #49.

## 1. Goal

Vocation standardizes collaboration with an external research-capable model/tool without requiring a direct paid LLM API.

The normal boundary remains explicit:

1. Vocation builds a versioned prompt from local Vocation-owned context;
2. the user previews and copies it to the external tool;
3. the external tool performs research and returns only the requested versioned JSON bundle;
4. Vocation validates, links provenance and applies the bundle through the correct import boundary.

Prompt generation is not research. External model output is not trusted Vocation state until it passes the versioned import pipeline.

## 2. Implemented workflow types

### Initial Research

For a new or expanded personal market.

Normal implemented input:

- explicit Search Profile or configured default;
- exact Search Profile revision/snapshot;
- optional current Candidate Profile revision/snapshot, included only after an explicit UI choice;
- as-of date;
- active Vocation evaluation/assessment context needed by the output contract;
- quality-first result target.

The generated prompt context stores an opaque `prompt_context_ref` and canonical expected Research Bundle 1.0 `research_scope`. The reference is internal workflow provenance and is not added to the frozen Research Bundle 1.0 schema.

Output:

- complete Research Bundle `1.0`;
- no Vocation-internal profile IDs;
- linked inline import may separately carry the `prompt_context_ref` so Vocation can verify that the returned scope matches the exact prompt snapshot.

Legacy/manual context-free Research Bundle 1.0 import remains supported.

### Full Update

For the entire known market.

Input:

- Vocation-generated Prompt Context Snapshot with opaque Correlation References;
- only the known-market context required by the update contract;
- open/missing evidence relevant to the requested update.

Output: Research Update Bundle `2.0`. Availability/Freshness is not silently folded into this contract.

### Company Update

Scope: one or more known Companies and their permitted descendants according to the versioned update contract.

### Opportunity Update

Scope: user-selected Opportunities; their Postings are permitted descendants according to the versioned update contract. A direct arbitrary Posting scope is not invented by the UI.

### Gap Filling

Scope: selected missing/uncertain fields or criterion evidence. It must not become an uncontrolled general re-research run.

### Availability Check

Scope: known Postings and only append-only Availability Observations according to Availability Check Bundle 1.0.

Availability/Freshness answers whether a Posting is currently evidenced as available, unavailable, uncertain or unknown. It does not delete historical Research evidence or create a permanent Opportunity-closed truth.

## 3. Initial Research quality policy

Initial Research is explicitly quality-first:

- prefer a smaller set of well-evidenced current Opportunities over filling the requested result target with weak matches;
- prioritize evidence needed by Search Profile hard constraints and high-value evaluation criteria;
- distinguish missing evidence from positive evidence;
- preserve source/reference provenance and observation times;
- do not ask the external tool to produce an opaque final Vocation ranking;
- do not expose or mutate private notes, personal Decisions, Tracking Status or application state.

## 4. Real-market source and freshness policy

Manual job-search work refined the source strategy beyond the earlier generic prompt wording.

Research prompts should:

- prefer an official company careers page or original employer posting when available;
- verify that a real application route is active close to the research/import date where practical;
- use aggregators/search engines as discovery sources without treating an old cached hit as proof that a Posting is still actionable;
- treat posting age as a warning/verification signal, not an automatic rejection;
- retain useful provenance for a stale/expired finding while allowing Availability evidence to remove it from the set of current actionable postings;
- inspect relevant company career pages broadly enough to find normal Developer, Young Professional, Trainee or adjacent role titles rather than requiring the literal word `Junior`;
- filter discovered roles for actual entry suitability and software-development relevance rather than title alone.

This policy does not turn Vocation into a crawler. The external research step remains user-initiated and explicit.

## 5. Planned Research Strategies / grinds

The currently implemented Initial Research mode does not yet model search coverage as several distinct strategies. #49 tracks this next product slice.

Planned strategy families include:

1. **Role-first discovery** – current role terms/aliases from the selected Search Profile;
2. **Company-first grind** – inspect a selected/uncovered company set and its official careers pages comprehensively;
3. **Domain/technology grind** – search concrete product/domain/technology clusters and then evaluate entry suitability;
4. **Regional grind** – intentionally cover one configured region/remote scope before expanding to another;
5. **Freshness re-check** – revisit known Posting URLs/application routes through the dedicated freshness/availability boundary;
6. **Gap/coverage grind** – deliberately search under-covered companies/roles/evidence rather than repeating already covered work.

These are planned prompt/run strategies, not new Research Bundle schemas by themselves. Existing frozen contracts remain unchanged unless a separate versioned contract decision proves necessary.

## 6. Company coverage direction

Company-first research needs durable coverage state even when no Opportunity is found.

#49 plans a Vocation-owned discovery/coverage view that can remember:

- company/careers URL under consideration;
- last checked/researched time and Prompt Run provenance;
- outcome such as relevant role found / no current relevant role / inaccessible / revisit required;
- selected or uncovered companies for another explicit research run.

A discovery/coverage company is not automatically promoted into an evidence-backed imported Opportunity. Contract/domain identity boundaries remain conservative.

## 7. Prompt package

A generated prompt package contains, as applicable:

1. clear task and research strategy;
2. explicit scope;
3. as-of date;
4. exact selected Search Profile and optional Candidate Profile snapshot for Initial Research;
5. Vocation-issued opaque Correlation References for update subjects;
6. generic protection rules for personal/private state;
7. open questions or requested gaps;
8. source/freshness/quality research requirements;
9. fully embedded expected output contract/schema guidance;
10. rule `JSON only`;
11. expected bundle version.

A rendered prompt must not rely on local repository paths.

## 8. Prompt context minimization and disclosure

Only data required by the selected workflow is embedded.

Not automatically included:

- complete unrelated Opportunity history;
- private notes;
- Personal Assessment/Decision/Tracking values unless a future explicitly accepted workflow requires and exposes them;
- unrelated Companies;
- database/internal implementation fields;
- CV/certificate/document content merely because it exists locally.

Candidate Profile inclusion in Initial Research is explicit. Future application-material prompts may intentionally include selected private profile/document context, but they require their own visible disclosure/preview boundary (#50).

## 9. Protected state

Research outputs must never create, overwrite or clear Vocation-owned private decision/application state merely because it appeared in a prompt context.

In particular, Research/Update output does not own:

- Personal Assessments;
- Decisions, Exclusion/Restore;
- Tracking Status;
- private Opportunity notes;
- Groups/Waves or future user-facing collection/application planning state;
- ApplicationCases, ApplicationMaterials or ApplicationDocuments;
- Candidate/Search Profile state.

## 10. Output rules

Every research prompt requires:

- valid JSON;
- no Markdown fences or explanatory prose around the payload;
- the exact expected versioned bundle type;
- explicit Research Scope;
- sources/references and times where the contract requires them;
- no invented Vocation-internal IDs;
- only correlation references supplied by the current Prompt Context when the update contract requires them;
- no unknown properties or ad-hoc assessment criteria;
- complete provenance required by the contract.

## 11. Update prompt rules

- do not repeat all known data when unchanged unless the contract requires it;
- prioritize changed/new/missing evidence;
- mark uncertainty explicitly;
- do not interpret a temporarily unreachable URL as permanent closure;
- never exceed the Prompt Context scope silently;
- echo only current snapshot-local Correlation References;
- Gap Filling returns only requested permitted evidence and does not create unrelated subjects;
- availability evidence uses the dedicated Availability Check workflow rather than inventing a second freshness model.

## 12. Current UI and manual-acceptance finding

The implemented desktop UI can choose prompt type/scope, preview/copy/save prompts and import returned JSON inline. Initial Research uses persistent Search Profiles and optional Candidate Profile inclusion.

The first manual product pass did not accept the surrounding navigation/form design. The prompt capability remains valid, but the user-facing Profile/Recherche flow and explicit strategy selection need the redesign tracked in #45/#47/#49. `docs/17_MANUAL_PRODUCT_ACCEPTANCE.md` is authoritative for that current product direction.

## 13. Templates

Current versioned templates include:

- `prompts/initial-research.md`
- `prompts/full-update.md`
- `prompts/company-update.md`
- `prompts/opportunity-update.md`
- `prompts/gap-filling.md`
- `prompts/availability-check.md`
- `prompts/output-contract.md`

New strategy templates/policies from #49 must preserve the same versioned/provenance discipline rather than becoming untracked ad-hoc prompts.

## 14. Privacy and safety

- no automatic sending to an external model/tool;
- user previews what is copied;
- no secrets or local file paths;
- no automatic application submission;
- no hidden CV/certificate disclosure;
- external research may propose data, but Vocation validates and owns accepted local state;
- future prompt-assisted catalog/profile/application generation requires explicit review before local mutation.
