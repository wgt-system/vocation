import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type ApplicationCase,
  type ApplicationMaterial,
} from "../../api/client";
import { ApplicationCasePanel } from "./ApplicationCasePanel";

vi.mock("../../api/client", () => ({
  api: {
    listApplicationCases: vi.fn(),
    createApplicationCase: vi.fn(),
    changeApplicationCaseLifecycle: vi.fn(),
    listApplicationMaterials: vi.fn(),
    createApplicationMaterial: vi.fn(),
    reviseApplicationMaterial: vi.fn(),
  },
}));

const baseCase = (
  overrides: Partial<ApplicationCase> = {},
): ApplicationCase => ({
  id: "case-1",
  opportunity_id: "opp-1",
  lifecycle: "draft",
  created_at: "2026-08-13T10:00:00Z",
  updated_at: "2026-08-13T10:00:00Z",
  lifecycle_events: [
    {
      previous_status: null,
      resulting_status: "draft",
      occurred_at: "2026-08-13T10:00:00Z",
    },
  ],
  ...overrides,
});

const material = (
  overrides: Partial<ApplicationMaterial> = {},
): ApplicationMaterial => ({
  id: "material-1",
  application_case_id: "case-1",
  kind: "cv",
  display_name: "Lebenslauf",
  revision: 1,
  created_at: "2026-08-13T10:00:00Z",
  updated_at: "2026-08-13T10:00:00Z",
  ...overrides,
});

beforeEach(() => {
  vi.mocked(api.listApplicationCases).mockResolvedValue([]);
  vi.mocked(api.listApplicationMaterials).mockResolvedValue([]);
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ApplicationCasePanel", () => {
  it("offers an explicit create action when there is no case", async () => {
    const user = userEvent.setup();
    const created = baseCase();
    vi.mocked(api.createApplicationCase).mockResolvedValue(created);
    vi.mocked(api.listApplicationCases)
      .mockResolvedValueOnce([])
      .mockResolvedValue([created]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    await user.click(
      await screen.findByRole("button", { name: "Bewerbung anlegen" }),
    );
    expect(api.createApplicationCase).toHaveBeenCalledWith("opp-1");
  });

  it("shows a created draft and initial lifecycle history", async () => {
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect((await screen.findAllByText(/Entwurf/)).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Entwurf ·/).length).toBeGreaterThan(0);
  });

  it("changes an active lifecycle and refreshes the case", async () => {
    const user = userEvent.setup();
    const draft = baseCase();
    const ready = baseCase({
      lifecycle: "ready",
      updated_at: "2026-08-13T11:00:00Z",
      lifecycle_events: [
        ...draft.lifecycle_events,
        {
          previous_status: "draft",
          resulting_status: "ready",
          occurred_at: "2026-08-13T11:00:00Z",
        },
      ],
    });
    vi.mocked(api.listApplicationCases)
      .mockResolvedValueOnce([draft])
      .mockResolvedValue([ready]);
    vi.mocked(api.changeApplicationCaseLifecycle).mockResolvedValue(ready);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    await user.selectOptions(
      await screen.findByLabelText("Neuer Bewerbungsstatus"),
      "ready",
    );
    await user.click(
      screen.getByRole("button", { name: "Lebenszyklus speichern" }),
    );
    expect(api.changeApplicationCaseLifecycle).toHaveBeenCalledWith(
      "case-1",
      "ready",
    );
    expect(
      await screen.findByText("Lebenszyklus gespeichert."),
    ).toBeInTheDocument();
  });

  it("keeps terminal cases selectable and lifecycle read-only", async () => {
    vi.mocked(api.listApplicationCases).mockResolvedValue([
      baseCase({ lifecycle: "accepted", id: "case-terminal" }),
    ]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect((await screen.findAllByText(/Angenommen/)).length).toBeGreaterThan(
      0,
    );
    expect(
      screen.queryByLabelText("Neuer Bewerbungsstatus"),
    ).not.toBeInTheDocument();
  });

  it("shows active and historical cases", async () => {
    vi.mocked(api.listApplicationCases).mockResolvedValue([
      baseCase(),
      baseCase({ id: "case-old", lifecycle: "rejected" }),
    ]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    const selector = await screen.findByLabelText("Bewerbung auswählen");
    expect(selector).toHaveTextContent("Entwurf");
    expect(selector).toHaveTextContent("Abgelehnt");
  });

  it("creates material metadata and shows revision 1", async () => {
    const user = userEvent.setup();
    const currentCase = baseCase();
    vi.mocked(api.listApplicationCases).mockResolvedValue([currentCase]);
    vi.mocked(api.createApplicationMaterial).mockResolvedValue(material());
    vi.mocked(api.listApplicationMaterials)
      .mockResolvedValueOnce([])
      .mockResolvedValue([material()]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    await user.type(
      await screen.findByLabelText("Name der Unterlage"),
      "Lebenslauf",
    );
    await user.click(screen.getByRole("button", { name: "Unterlage anlegen" }));
    expect(api.createApplicationMaterial).toHaveBeenCalledWith(
      "case-1",
      "cv",
      "Lebenslauf",
    );
    expect(await screen.findByText(/Revision 1/)).toBeInTheDocument();
  });

  it("refreshes a material revision to revision 2", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials)
      .mockResolvedValueOnce([material()])
      .mockResolvedValue([material({ display_name: "CV neu", revision: 2 })]);
    vi.mocked(api.reviseApplicationMaterial).mockResolvedValue(
      material({ display_name: "CV neu", revision: 2 }),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    const input = await screen.findByLabelText("Revision für Lebenslauf");
    await user.clear(input);
    await user.type(input, "CV neu");
    await user.click(
      screen.getByRole("button", { name: "Revision erstellen" }),
    );
    expect(api.reviseApplicationMaterial).toHaveBeenCalledWith(
      "material-1",
      "CV neu",
    );
    expect(await screen.findByText(/Revision 2/)).toBeInTheDocument();
  });

  it("keeps API errors local and exposes no file controls", async () => {
    vi.mocked(api.listApplicationCases).mockRejectedValue(
      new Error("cases failed"),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("cases failed");
    expect(
      screen.queryByRole("textbox", { name: /Datei|Upload|Pfad/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Upload|Render|Datei/i }),
    ).not.toBeInTheDocument();
  });
});
