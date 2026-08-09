import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type OpportunityDetail,
  type UpdatePromptOptions,
} from "../api/client";
import { OpportunityDetailView } from "./opportunities/OpportunityDetailView";
import { OpportunityList } from "./opportunities/OpportunityList";
import { PromptView } from "./prompts/PromptView";

vi.mock("../api/client", () => ({
  api: {
    getUpdatePromptOptions: vi.fn(),
    generateAvailabilityPrompt: vi.fn(),
    importAvailabilityText: vi.fn(),
    importText: vi.fn(),
    listOpportunities: vi.fn(),
    listGroups: vi.fn(),
    getOpportunity: vi.fn(),
    listCriteria: vi.fn(),
  },
}));

const options: UpdatePromptOptions = {
  companies: [{ id: "company-1", name: "Acme GmbH" }],
  opportunities: [
    { id: "opportunity-1", title: "Engineer", company_id: "company-1" },
  ],
  postings: [
    {
      id: "posting-1",
      title: "Engineer posting",
      company_id: "company-1",
      opportunity_id: "opportunity-1",
    },
    {
      id: "posting-2",
      title: "Second posting",
      company_id: "company-1",
      opportunity_id: "opportunity-1",
    },
  ],
  observation_types: ["technology_requirement", "task", "salary"],
};

const availabilityPrompt = {
  bundle_kind: "availability_check" as const,
  bundle_version: "1.0" as const,
  prompt_context_ref: "availability-ctx-1",
  prompt_run_id: "run-availability-1",
  prompt_text: "availability prompt",
  prompt_type: "availability_check" as const,
  prompt_version: "1.0" as const,
  research_scope: {},
};

function detailFixture(): OpportunityDetail {
  return {
    id: "opportunity-1",
    title: "Engineer",
    company: { id: "company-1", name: "Acme GmbH" },
    locations: [],
    postings: [
      {
        id: "posting-1",
        title: "Engineer posting",
        published_at: null,
        observed_at: "2026-08-08T10:00:00Z",
        availability: "unavailable",
        availability_age_days: 3,
        availability_last_checked_at: "2026-08-06T10:00:00Z",
        availability_history: [
          {
            id: "availability-1",
            import_id: "availability-import-1",
            result: "unavailable",
            observed_at: "2026-08-06T09:00:00Z",
            recorded_at: "2026-08-06T10:00:00Z",
            evidence_summary: "Listing returned 404",
          },
        ],
        source: { id: "source-1", name: "Careers", type: "company_careers" },
        source_reference: {
          id: "reference-1",
          url: "https://example.com/job",
          display_label: "Original",
          observed_at: "2026-08-08T10:00:00Z",
        },
      },
    ],
    sources: [],
    observations: [],
    assessments: [],
    external_assessments: [],
    personal_assessments: [],
    personal_assessment_history: [],
    decision_history: [],
    tracking_status: "new",
    availability: "uncertain",
    availability_age_days: 2,
    availability_last_checked_at: "2026-08-07T10:00:00Z",
    import_provenance: {
      import_id: "import-1",
      bundle_id: "bundle-1",
      fingerprint: "fingerprint",
      applied_at: "2026-08-08T10:00:00Z",
    },
  };
}

beforeEach(() => {
  vi.mocked(api.getUpdatePromptOptions).mockResolvedValue(options);
  vi.mocked(api.generateAvailabilityPrompt).mockResolvedValue(
    availabilityPrompt,
  );
  vi.mocked(api.listCriteria).mockResolvedValue([]);
  vi.mocked(api.listGroups).mockResolvedValue([]);
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Availability workflow", () => {
  it("generates an Availability Check from selected postings and imports through the availability endpoint", async () => {
    const user = userEvent.setup();
    const onImported = vi.fn();
    render(<PromptView onImported={onImported} />);
    await user.selectOptions(
      screen.getByLabelText("Prompt-Modus"),
      "availability_check",
    );
    await user.click(await screen.findByLabelText("Engineer posting"));
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateAvailabilityPrompt).toHaveBeenCalledWith({
      posting_ids: ["posting-1"],
      as_of_date: expect.any(String),
    });
    expect(await screen.findByText("Availability Check")).toBeInTheDocument();
    expect(screen.getByText("Prompt Context Ref:")).toBeInTheDocument();

    vi.mocked(api.importAvailabilityText).mockResolvedValue({
      import_kind: "availability_check",
      import_id: "availability-import-1",
      status: "applied",
      bundle_id: "bundle-availability-1",
      bundle_version: "1.0",
      prompt_context_ref: "availability-ctx-1",
      fingerprint: "fingerprint",
      counts: { postings: 1 },
      warnings: [],
      issues: [],
      duplicate_of_import_id: null,
    });
    fireEvent.change(screen.getByLabelText("Availability-Ergebnis JSON"), {
      target: { value: "{}" },
    });
    await user.click(
      screen.getByRole("button", { name: "Bundle validieren und importieren" }),
    );
    expect(await screen.findByText("Import erfolgreich")).toBeInTheDocument();
    expect(api.importAvailabilityText).toHaveBeenCalledWith("{}");
    expect(api.importText).not.toHaveBeenCalled();
    expect(onImported).toHaveBeenCalledTimes(1);
  });

  it("filters opportunity list by compact availability state and keeps age visible", async () => {
    vi.mocked(api.listOpportunities).mockResolvedValue([
      {
        id: "available",
        title: "Available job",
        company_name: "Acme",
        locations: [],
        posting_count: 1,
        assessment_count: 0,
        import_id: "i",
        imported_at: "2026-08-08",
        tracking_status: "new",
        availability: "available",
        availability_age_days: 1,
        availability_last_checked_at: "2026-08-08T10:00:00Z",
      },
      {
        id: "uncertain",
        title: "Uncertain job",
        company_name: "Acme",
        locations: [],
        posting_count: 1,
        assessment_count: 0,
        import_id: "i",
        imported_at: "2026-08-08",
        tracking_status: "new",
        availability: "uncertain",
        availability_age_days: null,
        availability_last_checked_at: null,
      },
      {
        id: "unknown",
        title: "Unknown job",
        company_name: "Acme",
        locations: [],
        posting_count: 1,
        assessment_count: 0,
        import_id: "i",
        imported_at: "2026-08-08",
        tracking_status: "new",
      },
    ]);
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    expect(await screen.findByText("Available job")).toBeInTheDocument();
    expect(screen.getAllByText("Verfügbar").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("1 Tage alt")).toBeInTheDocument();
    await user.selectOptions(
      screen.getByLabelText("Availability filtern"),
      "uncertain",
    );
    expect(screen.getByText("Uncertain job")).toBeInTheDocument();
    expect(screen.queryByText("Available job")).not.toBeInTheDocument();
  });

  it("shows aggregate availability, posting freshness and append-only history", async () => {
    vi.mocked(api.getOpportunity).mockResolvedValue(detailFixture());
    render(
      <OpportunityDetailView opportunityId="opportunity-1" onBack={vi.fn()} />,
    );
    expect(await screen.findByText("Unsicher")).toBeInTheDocument();
    expect(screen.getByText("2 Tage alt")).toBeInTheDocument();
    expect(screen.getByText("Nicht verfügbar")).toBeInTheDocument();
    expect(screen.getByText("Availability-Historie")).toBeInTheDocument();
    expect(screen.getByText(/Listing returned 404/)).toBeInTheDocument();
  });
});
