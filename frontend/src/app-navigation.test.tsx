import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

vi.mock("./features/opportunities/OpportunityList", () => ({
  OpportunityList: ({
    onOpenProfiles,
    onStartResearch,
  }: {
    onOpenProfiles?: () => void;
    onStartResearch?: () => void;
  }) => (
    <div>
      Stellenmarkt-Inhalt
      <button type="button" onClick={onOpenProfiles}>
        Profile öffnen
      </button>
      <button type="button" onClick={onStartResearch}>
        Recherche starten
      </button>
    </div>
  ),
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
  PromptView: ({ onImported }: { onImported: () => void }) => (
    <div>
      Recherche-Inhalt
      <button type="button" onClick={onImported}>
        Research-Import erfolgreich
      </button>
    </div>
  ),
}));
vi.mock("./features/workspace/OrganisationView", () => ({
  OrganisationView: () => <div>Bewerbungen-Inhalt</div>,
}));
vi.mock("./features/workspace/ToolsView", () => ({
  ToolsView: () => <div>Werkzeuge-Inhalt</div>,
}));

afterEach(() => {
  cleanup();
});

describe("product navigation", () => {
  it("uses intent-oriented primary areas and keeps technical tools secondary", () => {
    render(<App />);
    const navigation = screen.getByRole("navigation", {
      name: "Arbeitsbereiche",
    });

    expect(
      within(navigation).getByRole("button", { name: "Stellenmarkt" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Profile" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Recherche" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Bewerbungen" }),
    ).toBeInTheDocument();
    expect(
      within(navigation).getByRole("button", { name: "Werkzeuge" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("Nächster Schritt")).not.toBeInTheDocument();
    expect(
      screen.queryByText("Lokal · privat · nachvollziehbar"),
    ).not.toBeInTheDocument();
  });

  it("lets the empty-market actions open profiles or research without global workflow cards", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText("Stellenmarkt-Inhalt")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Profile öffnen" }));
    expect(screen.getByText("Profil-Inhalt")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Stellenmarkt" }));
    await user.click(
      screen.getByRole("button", { name: "Recherche starten" }),
    );
    expect(screen.getByText("Recherche-Inhalt")).toBeInTheDocument();
  });

  it("hands a successful inline research import directly to the market", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Recherche" }));
    expect(screen.getByText("Recherche-Inhalt")).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "Research-Import erfolgreich" }),
    );
    expect(screen.getByText("Stellenmarkt-Inhalt")).toBeInTheDocument();
  });

  it("keeps applications and tools directly reachable", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Bewerbungen" }));
    expect(screen.getByText("Bewerbungen-Inhalt")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Werkzeuge" }));
    expect(screen.getByText("Werkzeuge-Inhalt")).toBeInTheDocument();
  });
});
