import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api/client";
import { profileApi } from "../profiles/profileApi";
import { fitApi } from "./fitApi";
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
  },
}));

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([]);
  vi.mocked(profileApi.listSearchProfiles).mockResolvedValue([]);
  vi.mocked(fitApi.list).mockResolvedValue([]);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Stellenmarkt product workspace", () => {
  it("keeps analysis controls out of the empty state and offers focused entry actions", async () => {
    vi.mocked(api.listOpportunities).mockResolvedValue([]);
    const onStartResearch = vi.fn();
    const onOpenProfiles = vi.fn();
    const user = userEvent.setup();

    render(
      <OpportunityList
        refreshToken={0}
        onSelect={vi.fn()}
        onStartResearch={onStartResearch}
        onOpenProfiles={onOpenProfiles}
      />,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Baue deinen ersten Stellenmarkt auf",
      }),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText("Opportunities durchsuchen"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText("Harte Kriterien filtern"),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Opportunities")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Profile öffnen" }));
    expect(onOpenProfiles).toHaveBeenCalledOnce();
    await user.click(screen.getByRole("button", { name: "Recherche starten" }));
    expect(onStartResearch).toHaveBeenCalledOnce();
  });

  it("groups analysis controls below the page header once jobs exist", async () => {
    vi.mocked(api.listOpportunities).mockResolvedValue([
      {
        id: "opp-1",
        title: "Junior Developer",
        company_name: "Example GmbH",
        locations: ["Hamburg"],
        posting_count: 1,
        assessment_count: 0,
        import_id: "import-1",
        imported_at: "2026-08-18T08:00:00Z",
        tracking_status: "new",
      },
    ]);

    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);

    expect(
      await screen.findByRole("heading", { name: "Stellenmarkt" }),
    ).toBeInTheDocument();
    expect(screen.getByText("1 Stellen")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Opportunities durchsuchen"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Availability filtern")).toBeInTheDocument();
    expect(screen.getByText("Verfügbarkeit")).toBeInTheDocument();
    expect(screen.getByText("Sammlung")).toBeInTheDocument();
  });
});
