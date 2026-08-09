import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api, type UpdatePromptOptions } from "../../api/client";
import { ImportReportView } from "../imports/ImportReportView";
import { PromptView } from "./PromptView";

vi.mock("../../api/client", () => ({
  api: {
    generatePrompt: vi.fn(),
    getUpdatePromptOptions: vi.fn(),
    generateUpdatePrompt: vi.fn(),
    listCriteria: vi.fn(),
    importText: vi.fn(),
  },
}));

const options: UpdatePromptOptions = {
  companies: [
    { id: "company-1", name: "Acme GmbH" },
    { id: "company-2", name: "Other AG" },
  ],
  opportunities: [
    { id: "opportunity-1", title: "Python Engineer", company_id: "company-1" },
  ],
  postings: [
    {
      id: "posting-1",
      title: "Python Engineer posting",
      company_id: "company-1",
      opportunity_id: "opportunity-1",
    },
  ],
  observation_types: ["technology_requirement", "task", "salary"],
};
const criteria = [
  {
    criterion_id: "company-criterion",
    display_name: "Company Criterion",
    description: "",
    value_type: "text" as const,
    allowed_values: [],
    applicable_subject_type: "company" as const,
    active: true,
    display_order: 1,
    revision: 1,
  },
  {
    criterion_id: "opportunity-criterion",
    display_name: "Opportunity Criterion",
    description: "",
    value_type: "text" as const,
    allowed_values: [],
    applicable_subject_type: "opportunity" as const,
    active: true,
    display_order: 2,
    revision: 1,
  },
  {
    criterion_id: "inactive-company",
    display_name: "Inactive Criterion",
    description: "",
    value_type: "text" as const,
    allowed_values: [],
    applicable_subject_type: "company" as const,
    active: false,
    display_order: 3,
    revision: 1,
  },
];

const updatePrompt = {
  bundle_version: "2.0" as const,
  criteria_count: 2,
  prompt_context_ref: "ctx-123",
  prompt_run_id: "run-123",
  prompt_text: "generated update prompt",
  prompt_type: "full_update" as const,
  prompt_version: "2.1",
  research_scope: { type: "full_update" as const, as_of_date: "2026-08-09" },
};

beforeEach(() => {
  vi.mocked(api.getUpdatePromptOptions).mockResolvedValue(options);
  vi.mocked(api.listCriteria).mockResolvedValue(criteria);
  vi.mocked(api.generatePrompt).mockResolvedValue({
    prompt_run_id: "initial-run",
    prompt_text: "initial prompt",
    bundle_version: "1.0",
    criteria_count: 2,
  });
  vi.mocked(api.generateUpdatePrompt).mockResolvedValue(updatePrompt);
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
  });
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

async function chooseMode(label: string) {
  await userEvent.selectOptions(screen.getByLabelText("Prompt-Modus"), label);
  await screen.findByLabelText("Stichtag");
}

describe("Research Prompt workflow", () => {
  it("keeps Initial Research payload unchanged", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await user.type(screen.getByLabelText("Suchprofil"), "Python developer");
    await user.type(
      screen.getByLabelText("Constraints, eine pro Zeile"),
      "Remote\nNo agencies",
    );
    await user.click(
      screen.getByRole("button", { name: /Self-contained Prompt erzeugen/ }),
    );
    expect(api.generatePrompt).toHaveBeenCalledWith(
      expect.objectContaining({
        search_profile: "Python developer",
        constraints: ["Remote", "No agencies"],
      }),
    );
  });

  it("submits Full Update with only mode and date", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await chooseMode("full_update");
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateUpdatePrompt).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: "full_update",
        as_of_date: expect.any(String),
      }),
    );
    expect(
      vi.mocked(api.generateUpdatePrompt).mock.calls[0][0],
    ).not.toHaveProperty("selected_ids");
    expect(
      vi.mocked(api.generateUpdatePrompt).mock.calls[0][0],
    ).not.toHaveProperty("gap_requests");
  });

  it("requires and submits selected Companies without implicitly selecting unrelated options", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await chooseMode("company_update");
    expect(screen.getByLabelText("Acme GmbH")).not.toBeChecked();
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateUpdatePrompt).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Mindestens ein Eintrag",
    );
    await user.click(screen.getByLabelText("Acme GmbH"));
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateUpdatePrompt).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: "company_update",
        selected_ids: ["company-1"],
      }),
    );
  });

  it("submits Opportunity IDs and does not expose or send Posting IDs", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await chooseMode("opportunity_update");
    expect(screen.getByText(/Python Engineer — Acme GmbH/)).toBeInTheDocument();
    expect(
      screen.queryByText("Python Engineer posting"),
    ).not.toBeInTheDocument();
    await user.click(screen.getByLabelText(/Python Engineer — Acme GmbH/));
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateUpdatePrompt).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: "opportunity_update",
        selected_ids: ["opportunity-1"],
      }),
    );
    expect(
      vi.mocked(api.generateUpdatePrompt).mock.calls[0][0].selected_ids,
    ).not.toContain("posting-1");
  });

  it("builds an Observation Gap request and prevents duplicate exact requests", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await chooseMode("gap_filling");
    await user.click(
      screen.getByRole("button", { name: "Request hinzufügen" }),
    );
    await user.selectOptions(screen.getByLabelText("Subject"), "company-1");
    await user.selectOptions(
      screen.getByLabelText("Observation"),
      "technology_requirement",
    );
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(api.generateUpdatePrompt).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: "gap_filling",
        gap_requests: [
          {
            subject_id: "company-1",
            subject_type: "company",
            observation_type: "technology_requirement",
            criterion_id: null,
          },
        ],
      }),
    );
    vi.clearAllMocks();
    vi.mocked(api.getUpdatePromptOptions).mockResolvedValue(options);
    vi.mocked(api.listCriteria).mockResolvedValue(criteria);
    await user.click(
      screen.getByRole("button", { name: "Request hinzufügen" }),
    );
    await user.selectOptions(
      screen.getAllByLabelText("Subject")[1],
      "company-1",
    );
    await user.selectOptions(
      screen.getAllByLabelText("Observation")[1],
      "technology_requirement",
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Doppelte");
  });

  it("filters Gap Criterion choices by active subject type", async () => {
    const user = userEvent.setup();
    render(<PromptView />);
    await chooseMode("gap_filling");
    await user.click(
      screen.getByRole("button", { name: "Request hinzufügen" }),
    );
    await user.selectOptions(
      screen.getByLabelText("Evidence Kind"),
      "criterion",
    );
    expect(
      screen.getByRole("option", { name: "Company Criterion" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("option", { name: "Opportunity Criterion" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("option", { name: "Inactive Criterion" }),
    ).not.toBeInTheDocument();
    await user.selectOptions(
      screen.getByLabelText("Subject Type"),
      "opportunity",
    );
    expect(
      screen.getByRole("option", { name: "Opportunity Criterion" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("option", { name: "Company Criterion" }),
    ).not.toBeInTheDocument();
  });

  it("shows update metadata, clears stale preview on scope change, and copies exact text", async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
    render(<PromptView />);
    await chooseMode("full_update");
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    expect(screen.getByText(/Bundle Version:/)).toBeInTheDocument();
    expect(screen.getByText(/Prompt Context Ref:/)).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "In Zwischenablage kopieren" }),
    );
    expect(writeText).toHaveBeenCalledWith("generated update prompt");
    await user.clear(screen.getByLabelText("Stichtag"));
    await user.type(screen.getByLabelText("Stichtag"), "2026-08-10");
    expect(
      screen.queryByDisplayValue("generated update prompt"),
    ).not.toBeInTheDocument();
  });

  it("imports the generated result and only applied imports notify the caller", async () => {
    const user = userEvent.setup();
    const imported = vi.fn();
    render(<PromptView onImported={imported} />);
    await chooseMode("full_update");
    await user.click(screen.getByRole("button", { name: "Prompt erzeugen" }));
    vi.mocked(api.importText).mockResolvedValue({
      import_id: "import-1",
      status: "applied",
      bundle_id: "bundle-1",
      bundle_version: "2.0",
      prompt_context_ref: "ctx-123",
      fingerprint: "fp",
      counts: {},
      warnings: [],
      issues: [],
      duplicate_of_import_id: null,
    });
    fireEvent.change(screen.getByLabelText("Research-Ergebnis JSON"), {
      target: { value: "{}" },
    });
    await user.click(
      screen.getByRole("button", { name: "Bundle validieren und importieren" }),
    );
    expect(await screen.findByText("Import erfolgreich")).toBeInTheDocument();
    expect(imported).toHaveBeenCalledTimes(1);
    vi.mocked(api.importText).mockResolvedValue({
      import_id: "import-2",
      status: "duplicate",
      bundle_id: "bundle-1",
      bundle_version: "2.0",
      prompt_context_ref: "ctx-123",
      fingerprint: "fp",
      counts: {},
      warnings: [],
      issues: [],
      duplicate_of_import_id: "import-1",
    });
    await user.click(
      screen.getByRole("button", { name: "Bundle validieren und importieren" }),
    );
    expect(imported).toHaveBeenCalledTimes(1);
  });

  it("renders import traceability fields", () => {
    render(
      <ImportReportView
        report={{
          import_id: "import-1",
          status: "applied",
          bundle_id: "bundle-1",
          bundle_version: "2.0",
          prompt_context_ref: "ctx-123",
          fingerprint: "fp",
          counts: {},
          warnings: [],
          issues: [],
          duplicate_of_import_id: null,
        }}
      />,
    );
    expect(screen.getByText(/Bundle Version:/)).toBeInTheDocument();
    expect(screen.getByText(/Prompt Context Ref:/)).toBeInTheDocument();
  });
});
