import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

vi.mock("./features/opportunities/OpportunityList", () => ({
  OpportunityList: () => <div>Stellenmarkt-Inhalt</div>,
}));
vi.mock("./features/opportunities/OpportunityDetailView", () => ({
  OpportunityDetailView: () => <div>Opportunity-Detail</div>,
}));
vi.mock("./features/opportunities/OpportunityFitBreakdown", () => ({
  OpportunityDetailFitPanel: () => <div>Fit-Detail</div>,
}));
vi.mock("./features/opportunities/OpportunityNotePanel", () => ({
  OpportunityNotePanel: () => <div>Notiz-Detail</div>,
}));
vi.mock("./features/profiles/ProfileSearchView", () => ({
  ProfileSearchView: () => <div>Profil-Inhalt</div>,
}));
vi.mock("./features/prompts/PromptView", () => ({
  PromptView: () => <div>Recherche-Inhalt</div>,
}));
vi.mock("./features/workspace/OrganisationView", () => ({
  OrganisationView: () => <div>Organisation-Inhalt</div>,
}));
vi.mock("./features/workspace/ToolsView", () => ({
  ToolsView: () => <div>Werkzeuge-Inhalt</div>,
}));

afterEach(() => {
  cleanup();
});

describe("first-user navigation", () => {
  it("keeps workflow areas primary and implementation surfaces secondary", () => {
    render(<App />);
    const navigation = screen.getByRole("navigation", {
      name: "Arbeitsbereiche",
    });

    expect(
      within(navigation).getByRole("button", { name: "Stellenmarkt" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Profil & Suche" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Recherche" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Organisation" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Werkzeuge" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).queryByRole("button", { name: "Import" }),
    ).not.toBeInTheDocument();
    expect(
      within(navigation).queryByRole("button", { name: "Dubletten" }),
    ).not.toBeInTheDocument();
    expect(
      within(navigation).queryByRole("button", {
        name: "Assessment-Kriterien",
      }),
    ).not.toBeInTheDocument();
  });

  it("moves directly from market to profile and research and back", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText("Stellenmarkt-Inhalt")).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "Profil konfigurieren" }),
    );
    expect(screen.getByText("Profil-Inhalt")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Mit Profil recherchieren" }),
    );
    expect(screen.getByText("Recherche-Inhalt")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", { name: "Stellenmarkt öffnen" }),
    );
    expect(screen.getByText("Stellenmarkt-Inhalt")).toBeInTheDocument();
  });

  it("keeps organisation and tools reachable without promoting technical screens", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Organisation" }));
    expect(screen.getByText("Organisation-Inhalt")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Werkzeuge" }));
    expect(screen.getByText("Werkzeuge-Inhalt")).toBeInTheDocument();
  });
});
