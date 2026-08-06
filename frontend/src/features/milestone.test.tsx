import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../api/client";
import { CriteriaView } from "./criteria/CriteriaView";
import { ImportView } from "./imports/ImportView";
import { OpportunityDetailView } from "./opportunities/OpportunityDetailView";
import { OpportunityList } from "./opportunities/OpportunityList";
import { PromptView } from "./prompts/PromptView";

vi.mock("../api/client", () => ({
  api: {
    listCriteria: vi.fn(),
    createCriterion: vi.fn(),
    editCriterion: vi.fn(),
    activateCriterion: vi.fn(),
    reorderCriteria: vi.fn(),
    generatePrompt: vi.fn(),
    importText: vi.fn(),
    getImportReport: vi.fn(),
    listOpportunities: vi.fn(),
    getOpportunity: vi.fn(),
  },
}));

const criterion = {
  criterion_id: "junior_suitability",
  display_name: "Junior-Eignung",
  description: "Junior fit",
  value_type: "numeric" as const,
  numeric_min: 1,
  numeric_max: 5,
  allowed_values: [],
  applicable_subject_type: "opportunity" as const,
  active: true,
  display_order: 10,
  revision: 1,
};

beforeEach(() => {
  vi.mocked(api.listCriteria).mockResolvedValue([criterion]);
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
  });
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("first milestone UI", () => {
  it("renders the criteria list", async () => {
    render(<CriteriaView />);
    expect(await screen.findByText("Junior-Eignung")).toBeInTheDocument();
    expect(screen.getByText(/junior_suitability/)).toBeInTheDocument();
  });

  it("generates and copies a self-contained prompt", async () => {
    vi.mocked(api.generatePrompt).mockResolvedValue({
      prompt_run_id: "run-1",
      prompt_text: "complete prompt",
      bundle_version: "1.0",
      criteria_count: 1,
    });
    render(<PromptView />);
    await userEvent.type(screen.getByLabelText("Suchprofil"), "Junior Python");
    await userEvent.click(
      screen.getByRole("button", { name: /Self-contained Prompt erzeugen/i }),
    );
    expect(
      await screen.findByDisplayValue("complete prompt"),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("button", { name: /Zwischenablage/ }),
    );
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      "complete prompt",
    );
    expect(screen.getByText("Kopiert.")).toBeInTheDocument();
  });

  it("renders import validation errors", async () => {
    vi.mocked(api.importText).mockResolvedValue({
      import_id: "imp-bad",
      status: "rejected",
      bundle_id: "bad",
      fingerprint: "abc",
      counts: {},
      warnings: [],
      duplicate_of_import_id: null,
      issues: [
        {
          severity: "error",
          code: "INVALID_URL",
          path: "$.source_references[0].url",
          message: "HTTPS required",
        },
      ],
    });
    render(<ImportView onImported={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Research Bundle JSON"), {
      target: { value: "{}" },
    });
    await userEvent.click(
      screen.getByRole("button", { name: /validieren und importieren/ }),
    );
    expect(await screen.findByText("Import abgelehnt")).toBeInTheDocument();
    expect(screen.getByText("INVALID_URL")).toBeInTheDocument();
  });

  it("renders a successful import report", async () => {
    vi.mocked(api.importText).mockResolvedValue({
      import_id: "imp-ok",
      status: "applied",
      bundle_id: "bundle-1",
      fingerprint: "abc",
      counts: { opportunities: 1 },
      warnings: [],
      duplicate_of_import_id: null,
      issues: [],
    });
    const imported = vi.fn();
    render(<ImportView onImported={imported} />);
    fireEvent.change(screen.getByLabelText("Research Bundle JSON"), {
      target: { value: "{}" },
    });
    await userEvent.click(
      screen.getByRole("button", { name: /validieren und importieren/ }),
    );
    expect(await screen.findByText("Import erfolgreich")).toBeInTheDocument();
    expect(screen.getByText("bundle-1")).toBeInTheDocument();
    expect(imported).toHaveBeenCalled();
  });

  it("renders imported opportunities", async () => {
    vi.mocked(api.listOpportunities).mockResolvedValue([
      {
        id: "opp-1",
        title: "Junior Developer",
        company_name: "Example GmbH",
        locations: ["Hamburg"],
        posting_count: 1,
        assessment_count: 1,
        import_id: "imp-1",
        imported_at: "2026-08-06T17:00:00Z",
      },
    ]);
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    expect(await screen.findByText("Junior Developer")).toBeInTheDocument();
    expect(screen.getByText("Example GmbH")).toBeInTheDocument();
    expect(screen.getByText("Hamburg")).toBeInTheDocument();
  });

  it("renders opportunity sources and assessments", async () => {
    vi.mocked(api.getOpportunity).mockResolvedValue({
      id: "opp-1",
      title: "Junior Developer",
      company: { id: "cmp-1", name: "Example GmbH" },
      locations: [
        { label: "Hamburg", precision: "city", evidence_summary: "Posting" },
      ],
      postings: [
        {
          id: "post-1",
          title: "Junior Developer",
          published_at: "2026-08-01",
          observed_at: "2026-08-06T16:00:00Z",
          source: {
            id: "src-1",
            name: "Example Careers",
            type: "company_careers",
          },
          source_reference: {
            id: "ref-1",
            url: "https://example.com/job",
            display_label: "Original",
            observed_at: "2026-08-06T16:00:00Z",
          },
        },
      ],
      sources: [
        {
          id: "src-1",
          name: "Example Careers",
          type: "company_careers",
          base_url: "https://example.com",
        },
      ],
      observations: [],
      assessments: [
        {
          id: "ass-1",
          criterion_id: "junior_suitability",
          criterion_name: "Junior-Eignung",
          value: 5,
          origin: "external_research",
          reasoning: "Explicitly junior",
        },
      ],
      import_provenance: {
        import_id: "imp-1",
        bundle_id: "bundle-1",
        fingerprint: "abc",
        applied_at: "2026-08-06T17:00:00Z",
      },
    });
    render(<OpportunityDetailView opportunityId="opp-1" onBack={vi.fn()} />);
    expect(await screen.findByText(/Example Careers/)).toBeInTheDocument();
    expect(screen.getByText("Junior-Eignung")).toBeInTheDocument();
    expect(screen.getByText("https://example.com/job")).toBeInTheDocument();
  });
});
