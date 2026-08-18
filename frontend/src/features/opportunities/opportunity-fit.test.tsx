import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api/client";
import { profileApi, type SearchProfile } from "../profiles/profileApi";
import { fitApi, type OpportunityFit } from "./fitApi";
import { OpportunityDetailFitPanel } from "./OpportunityFitBreakdown";
import { OpportunityList } from "./OpportunityList";

vi.mock("../../api/client", () => ({
  api: {
    listOpportunities: vi.fn(),
    listGroups: vi.fn(),
    compareOpportunities: vi.fn(),
  },
}));

vi.mock("../profiles/profileApi", () => ({
  profileApi: {
    listSearchProfiles: vi.fn(),
  },
}));

vi.mock("./fitApi", () => ({
  fitApi: {
    list: vi.fn(),
    get: vi.fn(),
  },
}));

function fit(
  opportunityId: string,
  score: number,
  hardStatus: OpportunityFit["hard_constraint_status"] = "pass",
): OpportunityFit {
  return {
    opportunity_id: opportunityId,
    search_profile_id: "search-1",
    search_profile_revision: 3,
    candidate_profile_revision: null,
    hard_constraint_status: hardStatus,
    weighted_fit_score: score,
    evidence_completeness: 75,
    contributions: [
      {
        criterion_id: "technology_fit",
        criterion_name: "Technologie-Passung",
        weight: 2,
        required: hardStatus === "fail",
        status: "scored",
        value: "good",
        origin: "external_research",
        score,
        weighted_points: score * 2,
        explanation: `Technologie-Passung erklärt ${score} Prozent.`,
      },
    ],
    hard_failures:
      hardStatus === "fail"
        ? ["Technologie-Passung: harte Schwelle verfehlt"]
        : [],
    hard_unknowns: [],
    missing_evidence: [],
  };
}

function searchProfile(
  id: string,
  name: string,
  isDefault: boolean,
): SearchProfile {
  return {
    id,
    revision: 1,
    name,
    description: "",
    target_roles: [],
    seniority_targets: [],
    preferred_technologies: [],
    acceptable_technologies: [],
    avoided_technologies: [],
    target_locations: [],
    work_models: [],
    relocation_willing: false,
    employment_types: [],
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
    is_default: isDefault,
  };
}

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([]);
  vi.mocked(profileApi.listSearchProfiles).mockResolvedValue([
    searchProfile("search-1", "Hamburg quality", true),
    searchProfile("search-2", "Berlin Java", false),
  ]);
  vi.mocked(api.listOpportunities).mockResolvedValue([
    {
      id: "opp-low",
      title: "Role Low",
      company_name: "Low GmbH",
      locations: ["Hamburg"],
      posting_count: 1,
      assessment_count: 1,
      import_id: "import-1",
      imported_at: "2026-08-17T10:00:00Z",
      tracking_status: "new",
    },
    {
      id: "opp-high",
      title: "Role High",
      company_name: "High GmbH",
      locations: ["Hamburg"],
      posting_count: 1,
      assessment_count: 1,
      import_id: "import-1",
      imported_at: "2026-08-17T10:00:00Z",
      tracking_status: "new",
    },
  ]);
  vi.mocked(fitApi.list).mockResolvedValue([
    fit("opp-low", 40),
    fit("opp-high", 90, "fail"),
  ]);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("explainable opportunity fit UI", () => {
  it("shows fit separately from completeness, sorts scored opportunities and opens the breakdown", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <OpportunityList refreshToken={0} onSelect={vi.fn()} />,
    );

    expect(await screen.findByText("Fit 40%")).toBeInTheDocument();
    expect(screen.getByText("Fit 90%")).toBeInTheDocument();
    expect(screen.getAllByText("Evidenz 75%")).toHaveLength(2);
    expect(
      screen.getByText("Harte Kriterien nicht erfüllt"),
    ).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Opportunities sortieren"),
      "fit_desc",
    );
    const cards = container.querySelectorAll(".opportunity-card");
    expect(cards[0]).toHaveTextContent("Role High");
    expect(cards[1]).toHaveTextContent("Role Low");

    await user.click(
      screen.getAllByRole("button", { name: "Fit erklären" })[0],
    );
    expect(
      screen.getByText("Technologie-Passung erklärt 90 Prozent."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Technologie-Passung: harte Schwelle verfehlt"),
    ).toBeInTheDocument();
  });

  it("preselects the default Search Profile and reloads fit when it changes", async () => {
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);

    const profile = await screen.findByLabelText(
      "Search Profile für Opportunity-Analyse",
    );
    expect(profile).toHaveValue("search-1");
    await waitFor(() =>
      expect(fitApi.list).toHaveBeenCalledWith(
        ["opp-low", "opp-high"],
        "search-1",
      ),
    );

    await user.selectOptions(profile, "search-2");
    await waitFor(() =>
      expect(fitApi.list).toHaveBeenCalledWith(
        ["opp-low", "opp-high"],
        "search-2",
      ),
    );
  });

  it("composes workspace search and hard-constraint filters and resets them", async () => {
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    expect(await screen.findByText("Role Low")).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Harte Kriterien filtern"),
      "fail",
    );
    expect(screen.queryByText("Role Low")).not.toBeInTheDocument();
    expect(screen.getByText("Role High")).toBeInTheDocument();

    await user.type(screen.getByLabelText("Opportunities durchsuchen"), "Low");
    expect(
      screen.getByText("Keine passenden Opportunities"),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Analyse zurücksetzen" }),
    );
    expect(screen.getByText("Role Low")).toBeInTheDocument();
    expect(screen.getByText("Role High")).toBeInTheDocument();
  });

  it("uses the same breakdown on the detail screen", async () => {
    vi.mocked(fitApi.get).mockResolvedValue(fit("opp-high", 90, "fail"));
    render(<OpportunityDetailFitPanel opportunityId="opp-high" />);

    expect(await screen.findByText("Fit 90%")).toBeInTheDocument();
    expect(
      screen.getByText("Technologie-Passung erklärt 90 Prozent."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Provenienz: external_research"),
    ).toBeInTheDocument();
  });
});
