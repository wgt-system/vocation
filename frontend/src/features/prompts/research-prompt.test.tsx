import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api, type UpdatePromptOptions } from "../../api/client";
import { ImportReportView } from "../imports/ImportReportView";
import {
  profileApi,
  type CandidateProfile,
  type SearchProfile,
} from "../profiles/profileApi";
import { initialResearchApi } from "./initialResearchApi";
import { PromptView } from "./PromptView";

vi.mock("../../api/client", () => ({
  api: {
    getUpdatePromptOptions: vi.fn(),
    generateUpdatePrompt: vi.fn(),
    listCriteria: vi.fn(),
    importText: vi.fn(),
  },
}));

vi.mock("../profiles/profileApi", () => ({
  profileApi: {
    listSearchProfiles: vi.fn(),
    getCandidate: vi.fn(),
  },
}));

vi.mock("./initialResearchApi", () => ({
  initialResearchApi: {
    generate: vi.fn(),
    importText: vi.fn(),
  },
}));

const options: UpdatePromptOptions = {
  companies: [
    { id: "company-1", name: "Acme GmbH" },
    { id: "company-2", name: "Other AG" },
  ],
  opportunities: [
    {
      id: "opportunity-1",
      title: "Python Engineer",
      company_id: "company-1",
    },
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

const searchProfiles: SearchProfile[] = [
  {
    id: "search-1",
    revision: 2,
    name: "Hamburg quality",
    description: "Wenige gut belegte Junior-Stellen.",
    target_roles: ["Junior Softwareentwickler"],
    seniority_targets: ["junior"],
    preferred_technologies: ["Java"],
    acceptable_technologies: ["Python"],
    avoided_technologies: [],
    target_locations: ["Hamburg"],
    work_models: ["hybrid"],
    relocation_willing: false,
    employment_types: ["full-time"],
    preferred_industries: [],
    avoided_industries: [],
    preferred_company_characteristics: [],
    avoided_company_characteristics: [],
    salary_floor: null,
    salary_target: null,
    salary_currency: "EUR",
    must_haves: ["Berufseinstieg möglich"],
    must_not_haves: ["Senior-only"],
    result_limit: 6,
    criterion_policies: [],
    is_default: true,
  },
  {
    id: "search-2",
    revision: 1,
    name: "Berlin Java",
    description: "Alternative Suche.",
    target_roles: ["Softwareentwickler"],
    seniority_targets: [],
    preferred_technologies: ["Java"],
    acceptable_technologies: [],
    avoided_technologies: [],
    target_locations: ["Berlin"],
    work_models: [],
    relocation_willing: true,
    employment_types: ["full-time"],
    preferred_industries: [],
    avoided_industries: [],
    preferred_company_characteristics: [],
    avoided_company_characteristics: [],
    salary_floor: null,
    salary_target: null,
    salary_currency: "EUR",
    must_haves: [],
    must_not_haves: [],
    result_limit: 10,
    criterion_policies: [],
    is_default: false,
  },
];

const candidateProfile: CandidateProfile = {
  revision: 3,
  headline: "Junior Softwareentwickler",
  summary: "Informatikprofil mit Java-Erfahrung.",
  education: [],
  skills: [],
  languages: [],
  experience_summary: "",
  projects: [],
  interests: [],
};

const updatePrompt = {
  bundle_version: "2.0" as const,
  criteria_count: 2,
  prompt_context_ref: "ctx-123",
  prompt_run_id: "run-123",
  prompt_text: "generated update prompt",
  prompt_type: "full_update" as const,
  prompt_version: "2.1",
  research_scope: {
    type: "full_update" as const,
    as_of_date: "2026-08-09",
  },
};

beforeEach(() => {
  vi.mocked(api.getUpdatePromptOptions).mockResolvedValue(options);
  vi.mocked(api.listCriteria).mockResolvedValue(criteria);
  vi.mocked(profileApi.listSearchProfiles).mockResolvedValue(searchProfiles);
  vi.mocked(profileApi.getCandidate).mockResolvedValue(candidateProfile);
  vi.mocked(initialResearchApi.generate).mockResolvedValue({
    prompt_run_id: "initial-run",
    prompt_text: "profile-aware initial prompt",
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
  it("uses the default persistent Search Profile and visible Candidate disclosure for Initial Research", async () => {
    const user = userEvent.setup();
    render(<PromptView />);

    expect(
      screen.getByRole("heading", { name: "Recherche" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Neue Stellensuche" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", {
        name: "Gesamten Stellenmarkt aktualisieren",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Verfügbarkeit prüfen" }),
    ).toBeInTheDocument();

    const selector = await screen.findByLabelText("Search Profile");
    expect(selector).toHaveValue("search-1");
    expect(
      screen.getByText("Wenige gut belegte Junior-Stellen."),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Revision 2 · bis zu 6 Ergebnisse/),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText("Candidate Profile einbeziehen"),
    ).toBeChecked();
    expect(
      screen.getByText(/Revision 3 · Junior Softwareentwickler/),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Constraints, eine pro Zeile"),
    ).not.toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Profilbasierten Prompt erzeugen" }),
    );

    expect(initialResearchApi.generate).toHaveBeenCalledWith(
      expect.objectContaining({
        search_profile: "search-1",
        constraints: [],
        as_of_date: expect.any(String),
      }),
      true,
    );
    expect(screen.getByText(/Prompt Run:/)).toHaveTextContent("initial-run");
  });

  it("can select another Search Profile and exclude Candidate data explicitly", async () => {
    const user = userEvent.setup();
    render(<PromptView />);

    await screen.findByLabelText("Search Profile");
    await user.selectOptions(
      screen.getByLabelText("Search Profile"),
      "search-2",
    );
    await user.click(screen.getByLabelText("Candidate Profile einbeziehen"));
    await user.click(
      screen.getByRole("button", { name: "Profilbasierten Prompt erzeugen" }),
    );

    expect(initialResearchApi.generate).toHaveBeenCalledWith(
      expect.objectContaining({ search_profile: "search-2", constraints: [] }),
      false,
    );
  });

  it("links Initial Research inline import to the generated prompt run", async () => {
    const user = userEvent.setup();
    const imported = vi.fn();
    vi.mocked(initialResearchApi.importText).mockResolvedValue({
      import_id: "initial-import",
      status: "applied",
      bundle_id: "bundle-initial",
      bundle_version: "1.0",
      prompt_context_ref: "initial-ctx",
      fingerprint: "fp",
      counts: {},
      warnings: [],
      issues: [],
      duplicate_of_import_id: null,
    });
    render(<PromptView onImported={imported} />);

    await screen.findByLabelText("Search Profile");
    await user.click(
      screen.getByRole("button", { name: "Profilbasierten Prompt erzeugen" }),
    );
    fireEvent.change(screen.getByLabelText("Recherche-Ergebnis JSON"), {
      target: { value: "{}" },
    });
    await user.click(
      screen.getByRole("button", {
        name: "Bundle validieren und importieren",
      }),
    );

    expect(initialResearchApi.importText).toHaveBeenCalledWith(
      "{}",
      "initial-run",
    );
    expect(imported).toHaveBeenCalledTimes(1);
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
      screen.getByRole("button", { name: "Anfrage hinzufügen" }),
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
      screen.getByRole("button", { name: "Anfrage hinzufügen" }),
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
      screen.getByRole("button", { name: "Anfrage hinzufügen" }),
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
    fireEvent.change(screen.getByLabelText("Recherche-Ergebnis JSON"), {
      target: { value: "{}" },
    });
    await user.click(
      screen.getByRole("button", {
        name: "Bundle validieren und importieren",
      }),
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
      screen.getByRole("button", {
        name: "Bundle validieren und importieren",
      }),
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
