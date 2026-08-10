import type { ReactNode } from "react";

import type {
  ComparisonOpportunity,
  OpportunityComparison,
} from "../../api/client";

const dimensions = [
  ["technology_requirement", "Technologien"],
  ["task", "Aufgaben"],
  ["seniority", "Seniorität"],
  ["experience_requirement", "Erfahrung"],
  ["work_model", "Arbeitsmodell"],
  ["salary", "Gehalt"],
] as const;

const availabilityLabels = {
  available: "Verfügbar",
  unavailable: "Nicht verfügbar",
  uncertain: "Unsicher",
  unknown: "Unbekannt",
} as const;

function readableText(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }
  if (Array.isArray(value)) return value.map(readableText).join(", ");
  return JSON.stringify(value);
}

function readableValue(value: unknown): ReactNode {
  if (value !== null && typeof value === "object") {
    return <code>{readableText(value)}</code>;
  }
  return readableText(value);
}

function subjectLabel(subjectType: "opportunity" | "posting") {
  return subjectType === "opportunity" ? "Opportunity" : "Posting";
}

function freshness(opportunity: ComparisonOpportunity) {
  if (opportunity.availability_age_days !== null) {
    return `${opportunity.availability_age_days} Tage alt`;
  }
  if (opportunity.availability_last_checked_at) {
    return `geprüft ${new Date(opportunity.availability_last_checked_at).toLocaleString("de-DE")}`;
  }
  return "Alter unbekannt";
}

function EvidenceValues({
  opportunity,
  dimension,
}: {
  opportunity: ComparisonOpportunity;
  dimension: string;
}) {
  const cell = opportunity.research_dimensions[dimension];
  if (!cell || cell.state === "missing")
    return <span className="comparison-missing">Fehlend</span>;
  if (cell.values.length === 0) return <span>—</span>;
  return (
    <div className="comparison-values">
      {cell.values.map((item, index) => (
        <div
          className="comparison-evidence"
          key={`${item.subject_id}-${item.observed_at}-${index}`}
        >
          <strong>{readableValue(item.value)}</strong>
          <small>
            {new Date(item.observed_at).toLocaleString("de-DE")} ·{" "}
            {subjectLabel(item.subject_type)}
            {item.evidence_summary ? ` · ${item.evidence_summary}` : ""}
          </small>
        </div>
      ))}
    </div>
  );
}

function AssessmentCell({
  opportunity,
  criterionId,
  kind,
}: {
  opportunity: ComparisonOpportunity;
  criterionId: string;
  kind: "personal" | "external";
}) {
  if (kind === "personal") {
    const item = opportunity.personal_assessments.find(
      (assessment) => assessment.criterion_id === criterionId,
    );
    if (!item) return <span className="comparison-missing">Fehlend</span>;
    return (
      <div className="comparison-values">
        <strong>{readableValue(item.value)}</strong>
        {item.reasoning && <span>{item.reasoning}</span>}
        <small>{new Date(item.created_at).toLocaleString("de-DE")}</small>
      </div>
    );
  }
  const items = opportunity.external_assessments.filter(
    (assessment) => assessment.criterion_id === criterionId,
  );
  if (items.length === 0)
    return <span className="comparison-missing">Fehlend</span>;
  return (
    <div className="comparison-values">
      {items.map((item, index) => (
        <div
          className="comparison-evidence"
          key={`${item.criterion_id}-${item.created_at}-${index}`}
        >
          <strong>{readableValue(item.value)}</strong>
          {item.reasoning && <span>{item.reasoning}</span>}
          <small>{new Date(item.created_at).toLocaleString("de-DE")}</small>
        </div>
      ))}
    </div>
  );
}

export function OpportunityComparisonView({
  comparison,
  onBack,
  onSelect,
}: {
  comparison: OpportunityComparison;
  onBack: () => void;
  onSelect: (id: string) => void;
}) {
  return (
    <section>
      <button className="back" type="button" onClick={onBack}>
        ← Zurück zu Opportunities
      </button>
      <header className="page-header">
        <div>
          <p className="eyebrow">Read-only comparison</p>
          <h1>Opportunity-Vergleich</h1>
        </div>
      </header>
      <div className="comparison-scroll">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Zusammenfassung</th>
              {comparison.opportunities.map((opportunity) => (
                <th scope="col" key={opportunity.opportunity_id}>
                  <div className="comparison-column-heading">
                    <span className="eyebrow">{opportunity.company_name}</span>
                    <strong>{opportunity.title}</strong>
                    <button
                      type="button"
                      onClick={() => onSelect(opportunity.opportunity_id)}
                    >
                      Details
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Company</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>
                  {opportunity.company_name}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Title</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>{opportunity.title}</td>
              ))}
            </tr>
            <tr>
              <th scope="row">WorkLocations</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>
                  {opportunity.work_locations.length === 0
                    ? "Fehlend"
                    : opportunity.work_locations.map((location, index) => (
                        <div key={`${location.label}-${index}`}>
                          {location.label} <small>({location.precision})</small>
                        </div>
                      ))}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Tracking Status</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>
                  {opportunity.tracking_status}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Availability</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>
                  {availabilityLabels[opportunity.availability]}
                  <small>{freshness(opportunity)}</small>
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Groups/Waves</th>
              {comparison.opportunities.map((opportunity) => (
                <td key={opportunity.opportunity_id}>
                  {opportunity.groups.length === 0
                    ? "Fehlend"
                    : opportunity.groups.map((group) => group.name).join(" · ")}
                </td>
              ))}
            </tr>
            {dimensions.map(([key, label]) => (
              <tr key={key}>
                <th scope="row">{label}</th>
                {comparison.opportunities.map((opportunity) => (
                  <td key={opportunity.opportunity_id}>
                    <EvidenceValues opportunity={opportunity} dimension={key} />
                  </td>
                ))}
              </tr>
            ))}
            <tr className="comparison-section-row">
              <th colSpan={comparison.opportunities.length + 1}>
                Persönliche Assessments
              </th>
            </tr>
            {comparison.assessment_criteria.map((criterion) => (
              <tr key={`personal-${criterion.criterion_id}`}>
                <th scope="row">{criterion.display_name}</th>
                {comparison.opportunities.map((opportunity) => (
                  <td key={opportunity.opportunity_id}>
                    <AssessmentCell
                      opportunity={opportunity}
                      criterionId={criterion.criterion_id}
                      kind="personal"
                    />
                  </td>
                ))}
              </tr>
            ))}
            <tr className="comparison-section-row">
              <th colSpan={comparison.opportunities.length + 1}>
                Externe Assessments
              </th>
            </tr>
            {comparison.assessment_criteria.map((criterion) => (
              <tr key={`external-${criterion.criterion_id}`}>
                <th scope="row">{criterion.display_name}</th>
                {comparison.opportunities.map((opportunity) => (
                  <td key={opportunity.opportunity_id}>
                    <AssessmentCell
                      opportunity={opportunity}
                      criterionId={criterion.criterion_id}
                      kind="external"
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
