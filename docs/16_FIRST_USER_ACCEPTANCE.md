# First-user acceptance

**Status:** automated path passes; first manual product pass on 2026-08-18 is blocked by #45–#52.

This acceptance path verifies Vocation as a qualitative, local job-search workflow rather than as isolated implementation screens.

## Automated deterministic acceptance

`backend/tests/test_first_user_acceptance.py` runs the complete first-user path through the real FastAPI, application and persistence layers with `examples/acceptance/first-user-market.json`:

1. create a Candidate Profile;
2. create a default Search Profile with an explainable criterion policy;
3. generate an Initial Research prompt and retain exact profile/candidate provenance;
4. import a linked Research Bundle 1.0 containing several evidence-backed Opportunities;
5. evaluate those Opportunities with the selected Search Profile;
6. add private note, Tracking Status/Decision and Group/Wave state;
7. generate and apply a correlation-ref-based Opportunity Update Bundle 2.0;
8. verify personal state and original evidence survive the update;
9. restart the application against the same database and verify the workflow state again.

The fixture is intentionally synthetic and repository-stable. CI therefore tests Vocation deterministically and does not depend on websites, search engines, model availability or the current job market.

The currently implemented UI mirrors this sequence through **Stellenmarkt**, **Profil & Suche**, **Recherche** and **Organisation**. Manual raw import and direct criterion administration remain under **Werkzeuge**. A successful inline import from **Recherche** refreshes the market state and returns directly to **Stellenmarkt**.

This describes implementation, not the accepted final information architecture. The manual pass has since rejected parts of that presentation; see `17_MANUAL_PRODUCT_ACCEPTANCE.md` and #45.

## Manual acceptance result – 2026-08-18

The first real local/manual product pass **did not pass**. It stopped before a release decision because the normal empty-market/profile workflow already exposed blocking findings:

- global `Nächster Schritt` guidance duplicates navigation and should be removed;
- the sidebar footer slogan has no useful product function;
- Stellenmarkt title/count/search/filter/sort/view controls form an unreadable dense strip, including controls that are pointless for an empty market;
- mixed German/English user-facing terminology and inconsistent card/form sizing make the UI feel implementation-oriented;
- Candidate/Search Profile editing is too textarea-heavy and repetitive for durable use;
- Search Profile roles, seniority, employment types, industries and technologies need structured selectors; target locations need explicit place/radius semantics;
- the personal profile needs durable reusable personal/career facts and CV/certificate/evidence documents;
- `Organisation` and literal `Groups/Waves` are not accepted as final user-facing application-planning language;
- real research needs deliberate company-first/direct-career-page and freshness-verification strategies instead of one generic search pattern;
- the Windows development launcher hides backend failures and may make stale child/file-lock diagnosis unnecessarily difficult.

Focused blockers are tracked in #45–#52. Detailed product direction is in `17_MANUAL_PRODUCT_ACCEPTANCE.md`.

Because the product was already blocked at this stage, the current-market import/update/restart sequence below has **not yet been accepted**. It must be repeated after the blocking product work is resolved.

## Manual current-market acceptance procedure

When the blocking findings are ready for re-test, replace only the simulated external-research step with a real current research run:

1. Open the personal/search-profile area and review the Candidate Profile, default Search Profile and evaluation policy. Confirm target roles, technology tiers, search areas/work model, hard must/must-not constraints, result target and criterion policy.
2. Open **Recherche**, choose the intended initial-research strategy and confirm the Search Profile, optional Candidate Profile disclosure and today's as-of date.
3. Generate the prompt and copy it into a research-capable external model/tool. Do not manually add private Vocation state beyond what the prompt intentionally contains.
4. Ask the external tool to return only the requested schema-valid bundle. Prefer official company-career/original posting pages, verify an active application route where possible, and accept fewer results rather than quota-filling weak entries.
5. Paste the JSON into the inline result import on **Recherche**. The import must be accepted without editing internal IDs or provenance fields and should return to **Stellenmarkt**.
6. Verify that results show explainable Fit, evidence completeness and hard-constraint state for the selected Search Profile. Spot-check at least two Source Reference URLs against official current postings and their actual application path.
7. Exercise text search, Search Profile selection, hard-constraint/evidence filters, Fit sorting, map/comparison and the currently implemented collection/application-planning workflow. Add a private note and a Tracking Status/Decision to one Opportunity.
8. Return to **Recherche** and generate an Opportunity Update, Full Update or dedicated freshness/availability check for the current as-of date. Run it externally and import the returned versioned bundle.
9. Re-open the affected Opportunity. Confirm that new evidence was appended without replacing the original source provenance and that the private note, Tracking Status/Decision, collection membership and personal assessments remain intact.
10. Restart Vocation and confirm Candidate/Search Profiles plus the personal Opportunity/Application state are still present.

A failure in steps 5–10 is a Vocation acceptance failure. A current posting disappearing between research and manual verification is market volatility rather than an identity failure, but it must become visible through the existing Availability/Freshness workflow rather than remaining presented as an actionable current posting.

## Release rule

Automated acceptance plus a synthetic fixture is necessary but not sufficient. #42 closes only after the real local/current-market workflow has been exercised on the redesigned product, blocking findings are resolved or explicitly deferred, and the exact candidate passes the repository gates.
