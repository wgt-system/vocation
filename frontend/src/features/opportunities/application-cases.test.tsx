import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type ApplicationCase,
  type ApplicationDocument,
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
    getApplicationDocumentForMaterialRevision: vi.fn(),
    attachApplicationDocument: vi.fn(),
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

const document = (
  overrides: Partial<ApplicationDocument> = {},
): ApplicationDocument => ({
  id: "document-1",
  material_id: "material-1",
  material_revision: 1,
  original_filename: "resume.pdf",
  media_type: "application/pdf",
  byte_size: 1234,
  sha256: "secret-hash",
  created_at: "2026-08-13T10:00:00Z",
  ...overrides,
});

beforeEach(() => {
  vi.mocked(api.listApplicationCases).mockResolvedValue([]);
  vi.mocked(api.listApplicationMaterials).mockResolvedValue([]);
  vi.mocked(api.getApplicationDocumentForMaterialRevision).mockResolvedValue(
    null,
  );
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

  it("shows the file attachment UI for material without a document", async () => {
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([material()]);
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect(
      await screen.findByText("Noch keine Datei hinterlegt."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Datei hinterlegen" }),
    ).toBeInTheDocument();
  });

  it("loads exact material and current revision and shows existing metadata only", async () => {
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([
      material({ revision: 2 }),
    ]);
    vi.mocked(api.getApplicationDocumentForMaterialRevision).mockResolvedValue(
      document({ material_revision: 2 }),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect(await screen.findByText("Datei: resume.pdf")).toBeInTheDocument();
    expect(
      screen.getByText(/application\/pdf · 1234 Bytes/),
    ).toBeInTheDocument();
    expect(api.getApplicationDocumentForMaterialRevision).toHaveBeenCalledWith(
      "material-1",
      2,
    );
    expect(
      screen.queryByRole("button", { name: "Datei hinterlegen" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: /Revision ersetzen|Löschen|Download|Vorschau|Öffnen/,
      }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("secret-hash")).not.toBeInTheDocument();
  });

  it("uploads PDF bytes with the original filename and semantic media type", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([material()]);
    vi.mocked(api.attachApplicationDocument).mockResolvedValue(document());
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    const file = new File(["pdf bytes"], "resume.pdf", {
      type: "application/pdf",
    });
    await user.upload(
      await screen.findByLabelText("Datei für Lebenslauf"),
      file,
    );
    await user.click(screen.getByRole("button", { name: "Datei hinterlegen" }));
    const uploaded = vi.mocked(api.attachApplicationDocument).mock.calls[0][2];
    expect(uploaded.name).toBe("resume.pdf");
    expect(uploaded.type).toBe("application/pdf");
  });

  it("supports plain text and requires explicit Markdown selection when the browser MIME is unknown", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([material()]);
    vi.mocked(api.attachApplicationDocument).mockResolvedValue(
      document({ media_type: "text/markdown" }),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    const input = await screen.findByLabelText("Datei für Lebenslauf");
    const markdown = new File(["# heading"], "notes.md", { type: "" });
    await user.upload(input, markdown);
    expect(screen.getByLabelText("Medientyp für Lebenslauf")).toHaveValue("");
    await user.selectOptions(
      screen.getByLabelText("Medientyp für Lebenslauf"),
      "text/markdown",
    );
    await user.click(screen.getByRole("button", { name: "Datei hinterlegen" }));
    const uploaded = vi.mocked(api.attachApplicationDocument).mock.calls[0][2];
    expect(uploaded.name).toBe("notes.md");
    expect(uploaded.type).toBe("text/markdown");
  });

  it("replaces the no-document state after successful upload", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([material()]);
    vi.mocked(api.attachApplicationDocument).mockResolvedValue(document());
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    await user.upload(
      await screen.findByLabelText("Datei für Lebenslauf"),
      new File(["x"], "resume.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Datei hinterlegen" }));
    expect(await screen.findByText("Datei: resume.pdf")).toBeInTheDocument();
    expect(
      screen.queryByText("Noch keine Datei hinterlegt."),
    ).not.toBeInTheDocument();
  });

  it("keeps material and case UI visible when upload fails", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials).mockResolvedValue([material()]);
    vi.mocked(api.attachApplicationDocument).mockRejectedValue(
      new Error("upload failed"),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    await user.upload(
      await screen.findByLabelText("Datei für Lebenslauf"),
      new File(["x"], "resume.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Datei hinterlegen" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("upload failed");
    expect(screen.getByText("Lebenslauf · Revision 1")).toBeInTheDocument();
  });

  it("reloads document lookup for a new material revision without reusing revision one", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listApplicationCases).mockResolvedValue([baseCase()]);
    vi.mocked(api.listApplicationMaterials)
      .mockResolvedValueOnce([material()])
      .mockResolvedValue([material({ revision: 2, display_name: "CV neu" })]);
    vi.mocked(api.getApplicationDocumentForMaterialRevision)
      .mockResolvedValueOnce(document())
      .mockResolvedValueOnce(null);
    vi.mocked(api.reviseApplicationMaterial).mockResolvedValue(
      material({ revision: 2, display_name: "CV neu" }),
    );
    render(<ApplicationCasePanel opportunityId="opp-1" />);
    expect(await screen.findByText("Datei: resume.pdf")).toBeInTheDocument();
    await user.clear(screen.getByLabelText("Revision für Lebenslauf"));
    await user.type(screen.getByLabelText("Revision für Lebenslauf"), "CV neu");
    await user.click(
      screen.getByRole("button", { name: "Revision erstellen" }),
    );
    expect(
      api.getApplicationDocumentForMaterialRevision,
    ).toHaveBeenLastCalledWith("material-1", 2);
    expect(
      await screen.findByText("Noch keine Datei hinterlegt."),
    ).toBeInTheDocument();
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
