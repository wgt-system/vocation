import { describe, expect, it } from "vitest";

import type { OpportunityListItem } from "../../api/client";
import type { OpportunityFit } from "./fitApi";
import {
  analyzeOpportunities,
  type OpportunityWorkspaceFilters,
} from "./opportunityWorkspace";

function item(
  id: string,
  title: string,
  company: string,
  location: string,
  importedAt: string,
  trackingStatus: OpportunityListItem["tracking_status"] = "new",
  availability: OpportunityListItem["availability"] = "available",
): OpportunityListItem {
  return {
    id,
    title,
    company_name: company,
    locations: [location],
    posting_count: 1,
    assessment_count: 1,
    import_id: `import-${id}`,
    imported_at: importedAt,
    tracking_status: trackingStatus,
    availability,
  };
}

function fit(
  id: string,
  score: number | null,
  evidence: number,
  hard: OpportunityFit["hard_constraint_status"],
  missing: string[] = [],
): OpportunityFit {
  return {
    opportunity_id: id,
    search_profile_id: "profile-1",
    search_profile_revision: 1,
    candidate_profile_revision: null,
    hard_constraint_status: hard,
    weighted_fit_score: score,
    evidence_completeness: evidence,
    contributions: [],
    hard_failures: [],
    hard_unknowns: [],
    missing_evidence: missing,
  };
}

const items = [
  item(
    "opp-1",
    "Junior Java Developer",
    "Alpha GmbH",
    "Hamburg",
    "2026-08-18T08:00:00Z",
    "shortlisted",
  ),
  item(
    "opp-2",
    "Backend Engineer",
    "Beta AG",
    "Berlin",
    "2026-08-17T08:00:00Z",
    "to_review",
    "unknown",
  ),
  item(
    "opp-3",
    "Softwareentwickler",
    "Gamma GmbH",
    "Hamburg",
    "2026-08-16T08:00:00Z",
    "shortlisted",
  ),
];

const fits = {
  "opp-1": fit("opp-1", 88, 100, "pass"),
  "opp-2": fit("opp-2", 72, 60, "unknown", ["salary"]),
  "opp-3": fit("opp-3", 40, 80, "fail", ["seniority"]),
};

const defaults: OpportunityWorkspaceFilters = {
  query: "",
  statuses: [],
  availability: "all",
  hardConstraint: "all",
  evidence: "all",
  sort: "recency_desc",
};

describe("analyzeOpportunities", () => {
  it("searches title, company and location case-insensitively", () => {
    expect(
      analyzeOpportunities(items, fits, { ...defaults, query: "java" }).map(
        (entry) => entry.id,
      ),
    ).toEqual(["opp-1"]);
    expect(
      analyzeOpportunities(items, fits, { ...defaults, query: "BETA" }).map(
        (entry) => entry.id,
      ),
    ).toEqual(["opp-2"]);
    expect(
      analyzeOpportunities(items, fits, { ...defaults, query: "hamburg" }).map(
        (entry) => entry.id,
      ),
    ).toEqual(["opp-1", "opp-3"]);
  });

  it("composes status, availability, hard-constraint and evidence filters", () => {
    expect(
      analyzeOpportunities(items, fits, {
        ...defaults,
        statuses: ["shortlisted"],
        availability: "available",
        hardConstraint: "fail",
        evidence: "missing",
      }).map((entry) => entry.id),
    ).toEqual(["opp-3"]);
  });

  it("filters complete evidence separately from missing evidence", () => {
    expect(
      analyzeOpportunities(items, fits, {
        ...defaults,
        evidence: "complete",
      }).map((entry) => entry.id),
    ).toEqual(["opp-1"]);
  });

  it("sorts fit and evidence deterministically with unavailable fit last", () => {
    const partialFits = { "opp-1": fits["opp-1"], "opp-3": fits["opp-3"] };
    expect(
      analyzeOpportunities(items, partialFits, {
        ...defaults,
        sort: "fit_desc",
      }).map((entry) => entry.id),
    ).toEqual(["opp-1", "opp-3", "opp-2"]);
    expect(
      analyzeOpportunities(items, fits, {
        ...defaults,
        sort: "evidence_desc",
      }).map((entry) => entry.id),
    ).toEqual(["opp-1", "opp-3", "opp-2"]);
  });

  it("sorts by recency, company and title", () => {
    expect(
      analyzeOpportunities(items, fits, defaults).map((entry) => entry.id),
    ).toEqual(["opp-1", "opp-2", "opp-3"]);
    expect(
      analyzeOpportunities(items, fits, {
        ...defaults,
        sort: "company_asc",
      }).map((entry) => entry.id),
    ).toEqual(["opp-1", "opp-2", "opp-3"]);
    expect(
      analyzeOpportunities(items, fits, {
        ...defaults,
        sort: "title_asc",
      }).map((entry) => entry.id),
    ).toEqual(["opp-2", "opp-1", "opp-3"]);
  });
});
