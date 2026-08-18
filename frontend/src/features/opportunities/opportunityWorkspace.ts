import type { OpportunityListItem, TrackingStatus } from "../../api/client";
import type { OpportunityFit } from "./fitApi";

export type Availability = NonNullable<OpportunityListItem["availability"]>;
export type HardConstraintFilter =
  | "all"
  | OpportunityFit["hard_constraint_status"];
export type EvidenceFilter = "all" | "missing" | "complete";
export type OpportunitySort =
  | "recency_desc"
  | "fit_desc"
  | "evidence_desc"
  | "company_asc"
  | "title_asc";

export type OpportunityWorkspaceFilters = {
  query: string;
  statuses: TrackingStatus[];
  availability: Availability | "all";
  hardConstraint: HardConstraintFilter;
  evidence: EvidenceFilter;
  sort: OpportunitySort;
};

function availabilityOf(item: OpportunityListItem): Availability {
  return item.availability ?? "unknown";
}

function textMatches(item: OpportunityListItem, query: string): boolean {
  const normalized = query.trim().toLocaleLowerCase("de-DE");
  if (!normalized) return true;
  return [item.title, item.company_name, ...item.locations]
    .join("\n")
    .toLocaleLowerCase("de-DE")
    .includes(normalized);
}

function tieBreak(
  left: OpportunityListItem,
  right: OpportunityListItem,
): number {
  return (
    left.company_name.localeCompare(right.company_name, "de-DE") ||
    left.title.localeCompare(right.title, "de-DE") ||
    left.id.localeCompare(right.id)
  );
}

function scoreCompare(
  left: OpportunityListItem,
  right: OpportunityListItem,
  fits: Record<string, OpportunityFit>,
  value: (fit: OpportunityFit) => number | null,
): number {
  const leftFit = fits[left.id];
  const rightFit = fits[right.id];
  const leftScore = leftFit ? value(leftFit) : null;
  const rightScore = rightFit ? value(rightFit) : null;
  if (leftScore == null && rightScore == null) return tieBreak(left, right);
  if (leftScore == null) return 1;
  if (rightScore == null) return -1;
  return rightScore - leftScore || tieBreak(left, right);
}

export function analyzeOpportunities(
  items: OpportunityListItem[],
  fits: Record<string, OpportunityFit>,
  filters: OpportunityWorkspaceFilters,
): OpportunityListItem[] {
  const filtered = items.filter((item) => {
    const fit = fits[item.id];
    if (!textMatches(item, filters.query)) return false;
    if (
      filters.statuses.length > 0 &&
      !filters.statuses.includes(item.tracking_status)
    ) {
      return false;
    }
    if (
      filters.availability !== "all" &&
      availabilityOf(item) !== filters.availability
    ) {
      return false;
    }
    if (
      filters.hardConstraint !== "all" &&
      fit?.hard_constraint_status !== filters.hardConstraint
    ) {
      return false;
    }
    if (filters.evidence === "missing" && !fit?.missing_evidence.length) {
      return false;
    }
    if (
      filters.evidence === "complete" &&
      (!fit || fit.missing_evidence.length > 0)
    ) {
      return false;
    }
    return true;
  });

  return [...filtered].sort((left, right) => {
    switch (filters.sort) {
      case "fit_desc":
        return scoreCompare(left, right, fits, (fit) => fit.weighted_fit_score);
      case "evidence_desc":
        return scoreCompare(
          left,
          right,
          fits,
          (fit) => fit.evidence_completeness,
        );
      case "company_asc":
        return tieBreak(left, right);
      case "title_asc":
        return (
          left.title.localeCompare(right.title, "de-DE") ||
          left.company_name.localeCompare(right.company_name, "de-DE") ||
          left.id.localeCompare(right.id)
        );
      case "recency_desc":
        return (
          Date.parse(right.imported_at) - Date.parse(left.imported_at) ||
          tieBreak(left, right)
        );
    }
  });
}
