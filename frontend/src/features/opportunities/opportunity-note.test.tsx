import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { OpportunityNotePanel } from "./OpportunityNotePanel";
import { opportunityNoteApi } from "./opportunityNoteApi";

vi.mock("./opportunityNoteApi", () => ({
  opportunityNoteApi: {
    get: vi.fn(),
    save: vi.fn(),
  },
}));

beforeEach(() => {
  vi.mocked(opportunityNoteApi.get).mockResolvedValue({
    opportunity_id: "opp-1",
    content: "Existing private note",
    updated_at: "2026-08-18T00:00:00Z",
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("OpportunityNotePanel", () => {
  it("loads and saves a private opportunity note", async () => {
    vi.mocked(opportunityNoteApi.save).mockResolvedValue({
      opportunity_id: "opp-1",
      content: "Updated note",
      updated_at: "2026-08-18T01:00:00Z",
    });
    const user = userEvent.setup();
    render(<OpportunityNotePanel opportunityId="opp-1" />);

    const textarea = await screen.findByLabelText("Persönliche Opportunity-Notiz");
    expect(textarea).toHaveValue("Existing private note");
    await user.clear(textarea);
    await user.type(textarea, "Updated note");
    await user.click(screen.getByRole("button", { name: "Notiz speichern" }));

    expect(opportunityNoteApi.save).toHaveBeenCalledWith("opp-1", "Updated note");
    expect(await screen.findByText("Persönliche Notiz gespeichert.")).toBeInTheDocument();
    expect(textarea).toHaveValue("Updated note");
  });

  it("clears the editor when an empty note removes persistence", async () => {
    vi.mocked(opportunityNoteApi.save).mockResolvedValue(null);
    const user = userEvent.setup();
    render(<OpportunityNotePanel opportunityId="opp-1" />);

    const textarea = await screen.findByLabelText("Persönliche Opportunity-Notiz");
    await user.clear(textarea);
    await user.click(screen.getByRole("button", { name: "Notiz speichern" }));

    expect(await screen.findByText("Persönliche Notiz gelöscht.")).toBeInTheDocument();
    expect(textarea).toHaveValue("");
  });
});
