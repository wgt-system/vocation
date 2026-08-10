import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api, type Criterion, type OpportunityDetail } from "../../api/client";
import { OpportunityDetailView } from "./OpportunityDetailView";

vi.mock("../../api/client", () => ({
  api: {
    listCriteria: vi.fn(),
    getOpportunity: vi.fn(),
    listExternalLinks: vi.fn(),
    openExternalLink: vi.fn(),
    createPersonalAssessment: vi.fn(),
    revisePersonalAssessment: vi.fn(),
    changeStatus: vi.fn(),
    exclude: vi.fn(),
    restore: vi.fn(),
  },
}));

const criteria: Criterion[] = [
  {
    criterion_id: "score",
    display_name: "Score",
    description: "Score",
    value_type: "numeric",
    numeric_min: 10,
    numeric_max: 20,
    allowed_values: [],
    applicable_subject_type: "opportunity",
    active: true,
    display_order: 1,
    revision: 1,
  },
  {
    criterion_id: "work_model",
    display_name: "Arbeitsmodell",
    description: "Work model",
    value_type: "categorical",
    numeric_min: null,
    numeric_max: null,
    allowed_values: ["remote", "hybrid"],
    applicable_subject_type: "opportunity",
    active: true,
    display_order: 2,
    revision: 1,
  },
  {
    criterion_id: "visa",
    display_name: "Visa",
    description: "Visa",
    value_type: "boolean",
    numeric_min: null,
    numeric_max: null,
    allowed_values: [],
    applicable_subject_type: "opportunity",
    active: true,
    display_order: 3,
    revision: 1,
  },
  {
    criterion_id: "note",
    display_name: "Notiz",
    description: "Note",
    value_type: "text",
    numeric_min: null,
    numeric_max: null,
    allowed_values: [],
    applicable_subject_type: "opportunity",
    active: true,
    display_order: 4,
    revision: 1,
  },
];

function assessment(
  id: string,
  criterion_id: string,
  criterion_name: string,
  value: unknown,
  revision_number: number,
) {
  return {
    id,
    opportunity_id: "opp-1",
    criterion_id,
    criterion_name,
    value,
    reasoning: null,
    origin: "personal",
    revision_number,
    supersedes_id: null,
    created_at: `2026-08-0${revision_number}T10:00:00Z`,
  };
}

function makeDetail(
  tracking_status: OpportunityDetail["tracking_status"] = "new",
  personal_assessments: OpportunityDetail["personal_assessments"] = [],
  personal_assessment_history: OpportunityDetail["personal_assessment_history"] = [],
): OpportunityDetail {
  return {
    id: "opp-1",
    title: "Test Opportunity",
    company: { id: "company-1", name: "Example GmbH" },
    locations: [],
    postings: [],
    sources: [],
    observations: [],
    assessments: [],
    external_assessments: [],
    personal_assessments,
    personal_assessment_history,
    decision_history: [
      {
        id: "decision-1",
        opportunity_id: "opp-1",
        decision_type: "status_change",
        previous_status: "new",
        resulting_status: "interesting",
        reason: "Good fit",
        created_at: "2026-08-08T10:00:00Z",
        reverses_decision_id: null,
      },
    ],
    tracking_status,
    import_provenance: {
      import_id: "import-1",
      bundle_id: "bundle-1",
      fingerprint: "fingerprint",
      applied_at: "2026-08-08T09:00:00Z",
    },
  };
}

function renderDetail(detail = makeDetail()) {
  vi.mocked(api.getOpportunity).mockResolvedValue(detail);
  vi.mocked(api.listCriteria).mockResolvedValue(criteria);
  return render(
    <OpportunityDetailView opportunityId="opp-1" onBack={vi.fn()} />,
  );
}

beforeEach(() => {
  vi.mocked(api.listExternalLinks).mockResolvedValue([]);
  vi.mocked(api.createPersonalAssessment).mockResolvedValue({} as never);
  vi.mocked(api.revisePersonalAssessment).mockResolvedValue({} as never);
  vi.mocked(api.changeStatus).mockResolvedValue({} as never);
  vi.mocked(api.exclude).mockResolvedValue({} as never);
  vi.mocked(api.restore).mockResolvedValue({} as never);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Personal Triage UI", () => {
  it("uses configured numeric bounds and sends categorical, boolean and text values with their real types", async () => {
    const user = userEvent.setup();
    renderDetail();
    const numeric = await screen.findByLabelText("Wert");
    expect(numeric).toHaveAttribute("min", "10");
    expect(numeric).toHaveAttribute("max", "20");
    await user.click(
      screen.getByRole("button", { name: "Assessment erstellen" }),
    );
    expect(api.createPersonalAssessment).toHaveBeenCalledWith(
      "opp-1",
      expect.objectContaining({ criterion_id: "score", value: 10 }),
    );

    await user.selectOptions(screen.getByLabelText("Kriterium"), "work_model");
    await user.selectOptions(screen.getByLabelText("Wert"), "remote");
    await user.click(
      screen.getByRole("button", { name: "Assessment erstellen" }),
    );
    expect(api.createPersonalAssessment).toHaveBeenCalledWith(
      "opp-1",
      expect.objectContaining({ criterion_id: "work_model", value: "remote" }),
    );

    await user.selectOptions(screen.getByLabelText("Kriterium"), "visa");
    await user.selectOptions(screen.getByLabelText("Wert"), "true");
    await user.click(
      screen.getByRole("button", { name: "Assessment erstellen" }),
    );
    expect(api.createPersonalAssessment).toHaveBeenCalledWith(
      "opp-1",
      expect.objectContaining({ criterion_id: "visa", value: true }),
    );

    await user.selectOptions(screen.getByLabelText("Kriterium"), "note");
    await user.type(screen.getByLabelText("Wert"), "hello");
    await user.click(
      screen.getByRole("button", { name: "Assessment erstellen" }),
    );
    expect(api.createPersonalAssessment).toHaveBeenCalledWith(
      "opp-1",
      expect.objectContaining({ criterion_id: "note", value: "hello" }),
    );
  });

  it("initializes revisions from current values and calls revise, while labeling all current IDs", async () => {
    const currentScore = assessment("score-current", "score", "Score", 19, 2);
    const currentWorkModel = assessment(
      "work-current",
      "work_model",
      "Arbeitsmodell",
      "hybrid",
      2,
    );
    const historical = assessment(
      "work-old",
      "work_model",
      "Arbeitsmodell",
      "remote",
      1,
    );
    renderDetail(
      makeDetail(
        "new",
        [currentScore, currentWorkModel],
        [historical, currentScore, currentWorkModel],
      ),
    );
    expect(await screen.findByDisplayValue("19")).toBeInTheDocument();
    expect(
      screen.getByText("Score · Revision 2 (aktuell)"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Arbeitsmodell · Revision 2 (aktuell)"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Arbeitsmodell · Revision 1 (historisch)"),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("button", { name: "Revision erstellen" }),
    );
    expect(api.revisePersonalAssessment).toHaveBeenCalledWith(
      "opp-1",
      "score-current",
      expect.objectContaining({ value: 19 }),
    );
    expect(api.createPersonalAssessment).not.toHaveBeenCalled();
  });

  it("offers all direct targets only when active and keeps decision history visible", async () => {
    renderDetail();
    for (const label of [
      "Neu",
      "Zu prüfen",
      "Interessant",
      "Shortlist",
      "Später",
      "Archiviert",
    ]) {
      expect(
        await screen.findByRole("button", { name: label }),
      ).toBeInTheDocument();
    }
    expect(
      screen.queryByRole("button", { name: "excluded" }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/status_change: new/)).toBeInTheDocument();
  });

  it("separates status and exclusion reasons and blocks blank exclusion", async () => {
    const user = userEvent.setup();
    renderDetail();
    await screen.findByText("Test Opportunity");
    expect(screen.getByLabelText("Statusgrund (optional)")).toBeInTheDocument();
    const exclusion = screen.getByLabelText("Ausschlussgrund (erforderlich)");
    await user.type(exclusion, "   ");
    await user.click(screen.getByRole("button", { name: "Ausschließen" }));
    expect(api.exclude).not.toHaveBeenCalled();
    await user.clear(exclusion);
    await user.type(exclusion, "Not a fit");
    await user.click(screen.getByRole("button", { name: "Ausschließen" }));
    expect(api.exclude).toHaveBeenCalledWith("opp-1", "Not a fit");
  });

  it("shows only Restore for excluded opportunities and uses backend default restore", async () => {
    const user = userEvent.setup();
    renderDetail(makeDetail("excluded"));
    expect(
      await screen.findByRole("button", { name: "Restore" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Interessant" }),
    ).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Restore" }));
    expect(api.restore).toHaveBeenCalledWith("opp-1");
  });

  it("keeps the loaded opportunity visible when a mutation fails", async () => {
    vi.mocked(api.changeStatus).mockRejectedValue(new Error("Status failed"));
    renderDetail();
    await userEvent.click(
      await screen.findByRole("button", { name: "Interessant" }),
    );
    expect(await screen.findByText("Test Opportunity")).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("Status failed");
  });
});
