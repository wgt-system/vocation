import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type OpportunityComparison,
  type OpportunityListItem,
} from "../api/client";
import { OpportunityList } from "./opportunities/OpportunityList";
import { OpportunityComparisonView } from "./opportunities/OpportunityComparisonView";

vi.mock("../api/client", () => ({
  api: {
    listOpportunities: vi.fn(),
    listGroups: vi.fn(),
    compareOpportunities: vi.fn(),
  },
}));

function item(id: string, title: string): OpportunityListItem {
  return {
    id,
    title,
    company_name: `Company ${id}`,
    locations: [],
    posting_count: 1,
    assessment_count: 0,
    import_id: "import-1",
    imported_at: "2026-08-10T10:00:00Z",
    tracking_status: "new",
  };
}

const comparison: OpportunityComparison = {
  assessment_criteria: [
    { criterion_id: "fit", display_name: "Fit", display_order: 1 },
  ],
  opportunities: [
    {
      opportunity_id: "opp-2",
      company_id: "company-2",
      company_name: "Company opp-2",
      title: "Second",
      tracking_status: "new",
      availability: "available",
      availability_age_days: 2,
      availability_last_checked_at: "2026-08-08T10:00:00Z",
      groups: [],
      work_locations: [{ label: "Berlin", precision: "city" }],
      research_dimensions: {
        technology_requirement: {
          state: "present",
          values: [
            {
              value: "Python",
              observed_at: "2026-08-10T10:00:00Z",
              subject_id: "opp-2",
              subject_type: "opportunity",
              evidence_summary: "Stack",
            },
            {
              value: "PostgreSQL",
              observed_at: "2026-08-10T10:00:00Z",
              subject_id: "posting-2",
              subject_type: "posting",
              evidence_summary: null,
            },
          ],
        },
        task: { state: "missing", values: [] },
      },
      personal_assessments: [],
      external_assessments: [],
    },
    {
      opportunity_id: "opp-1",
      company_id: "company-1",
      company_name: "Company opp-1",
      title: "First",
      tracking_status: "shortlisted",
      availability: "unknown",
      availability_age_days: null,
      availability_last_checked_at: null,
      groups: [],
      work_locations: [],
      research_dimensions: {},
      personal_assessments: [
        {
          criterion_id: "fit",
          value: 8,
          reasoning: "Strong fit",
          created_at: "2026-08-09T10:00:00Z",
        },
      ],
      external_assessments: [
        {
          criterion_id: "fit",
          value: 7,
          reasoning: null,
          created_at: "2026-08-08T10:00:00Z",
        },
      ],
    },
  ],
};

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([]);
  vi.mocked(api.listOpportunities).mockResolvedValue([
    item("opp-1", "First"),
    item("opp-2", "Second"),
    item("opp-3", "Third"),
    item("opp-4", "Fourth"),
    item("opp-5", "Fifth"),
  ]);
  vi.mocked(api.compareOpportunities).mockResolvedValue(comparison);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Opportunity comparison workflow", () => {
  it("preserves selection order, permits removal, and prevents a fifth selection", async () => {
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    await screen.findByText("First");
    for (const label of [
      "Für Vergleich auswählen: Company opp-1 – First",
      "Für Vergleich auswählen: Company opp-2 – Second",
      "Für Vergleich auswählen: Company opp-3 – Third",
      "Für Vergleich auswählen: Company opp-4 – Fourth",
    ]) {
      await user.click(screen.getByLabelText(label));
    }
    const fifth = screen.getByLabelText(
      "Für Vergleich auswählen: Company opp-5 – Fifth",
    );
    expect(fifth).toBeDisabled();
    expect(
      screen.getByText("4 von 2–4 Opportunities ausgewählt"),
    ).toBeInTheDocument();
    await user.click(screen.getAllByRole("button", { name: "Entfernen" })[0]);
    expect(
      screen.getAllByRole("checkbox", { name: /Für Vergleich auswählen/ })[0],
    ).not.toBeChecked();
  });

  it("posts the exact selection order and keeps backend column order with Details", async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={onSelect} />);
    await screen.findByText("First");
    await user.click(
      screen.getByLabelText("Für Vergleich auswählen: Company opp-2 – Second"),
    );
    await user.click(
      screen.getByLabelText("Für Vergleich auswählen: Company opp-1 – First"),
    );
    await user.click(screen.getByRole("button", { name: "Vergleichen" }));
    expect(api.compareOpportunities).toHaveBeenCalledWith(["opp-2", "opp-1"]);
    const titles = Array.from(
      document.querySelectorAll(".comparison-column-heading strong"),
    ).map((element) => element.textContent);
    expect(titles.indexOf("Second")).toBeLessThan(titles.indexOf("First"));
    await user.click(screen.getAllByRole("button", { name: "Details" })[0]);
    expect(onSelect).toHaveBeenCalledWith("opp-2");
  });

  it("renders missing research data, separate evidence values, and aligned assessments", () => {
    render(
      <OpportunityComparisonView
        comparison={comparison}
        onBack={vi.fn()}
        onSelect={vi.fn()}
      />,
    );
    expect(screen.getAllByText("Fehlend").length).toBeGreaterThan(0);
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("Strong fit")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
  });
});
