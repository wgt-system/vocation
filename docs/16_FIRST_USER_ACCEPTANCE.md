# First-user acceptance

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

The normal UI mirrors this sequence: **Stellenmarkt**, **Profil & Suche**, **Recherche** and **Organisation** are the primary work areas. Manual raw import and direct criterion administration remain under **Werkzeuge**. A successful inline import from **Recherche** refreshes the market state and returns directly to **Stellenmarkt**.

## Manual current-market acceptance

Periodically replace only the simulated external-research step with a real current research run:

1. Open **Profil & Suche** and review the Candidate Profile and the default Search Profile. Confirm target roles, technology tiers, locations/work model, hard must/must-not constraints, result limit and criterion policy.
2. Open **Recherche**, choose **Initial Research**, confirm the intended Search Profile and whether Candidate Profile data should be included, and set today's as-of date.
3. Generate the prompt and copy it into a research-capable external model/tool. Do not manually add private Vocation state beyond what the prompt intentionally contains.
4. Ask the external tool to return only the requested Research Bundle JSON. Prefer official company-career pages as evidence and accept fewer results rather than quota-filling weak entries.
5. Paste the JSON into the inline result import on **Recherche**. The import must be accepted without editing internal IDs or provenance fields and should return directly to **Stellenmarkt**.
6. Verify that results show explainable Fit, evidence completeness and hard-constraint state for the selected Search Profile. Spot-check at least two Source Reference URLs against their official postings.
7. Exercise text search, Search Profile selection, hard-constraint/evidence filters, Fit sorting, map/comparison and a Group/Wave. Add a private note and a Tracking Status/Decision to one Opportunity.
8. Return to **Recherche** and generate an Opportunity Update or Full Update for the current as-of date. Run it externally and import the returned Bundle 2.0.
9. Re-open the affected Opportunity. Confirm that new evidence was appended without replacing the original source provenance and that the private note, Tracking Status/Decision, Group/Wave membership and personal assessments remain intact.
10. Restart Vocation and confirm Candidate/Search Profiles plus the personal Opportunity state are still present.

A failure in steps 5–10 is a Vocation acceptance failure. A current posting disappearing between research and manual verification is market volatility, not by itself an application failure; its availability should instead be refreshed through the dedicated availability/update workflow.
