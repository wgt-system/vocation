import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SearchVocabularyManager } from "./SearchVocabularyManager";
import { searchVocabularyApi } from "./searchVocabularyApi";

vi.mock("./searchVocabularyApi", async () => {
  const actual = await vi.importActual<typeof import("./searchVocabularyApi")>(
    "./searchVocabularyApi",
  );
  return {
    ...actual,
    searchVocabularyApi: {
      list: vi.fn(),
      createCustom: vi.fn(),
      update: vi.fn(),
      generateRefreshPrompt: vi.fn(),
      reviewProposals: vi.fn(),
    },
  };
});

beforeEach(() => {
  vi.mocked(searchVocabularyApi.list).mockResolvedValue([
    {
      id: "role-ai-engineer",
      kind: "role",
      label: "AI Engineer",
      aliases: ["Artificial Intelligence Engineer"],
      group: "AI & Data",
      is_active: true,
      is_custom: false,
    },
  ]);
  vi.mocked(searchVocabularyApi.createCustom).mockResolvedValue({
    id: "role-agentic",
    kind: "role",
    label: "Agentic Systems Engineer",
    aliases: [],
    group: "AI & Data",
    is_active: true,
    is_custom: true,
  });
  vi.mocked(searchVocabularyApi.update).mockImplementation(
    async (id, payload) => ({
      id,
      kind: "role",
      label: "AI Engineer",
      aliases: [],
      group: "AI & Data",
      is_active: payload.is_active ?? true,
      is_custom: false,
    }),
  );
  vi.mocked(searchVocabularyApi.generateRefreshPrompt).mockResolvedValue({
    prompt_version: "1.0",
    as_of_date: "2026-08-18",
    kinds: ["role", "technology", "industry"],
    prompt_text: "RESEARCH CURRENT VOCABULARY",
  });
  vi.mocked(searchVocabularyApi.reviewProposals).mockResolvedValue({
    contract: "vocation.search-vocabulary-proposals",
    version: "1.0",
    as_of_date: "2026-08-18",
    proposals: [
      {
        proposal: {
          kind: "role",
          label: "Agentic Systems Engineer",
          aliases: ["Agentic AI Engineer"],
          group: "AI & Data",
          reason: "Current market terminology.",
          source_urls: ["https://example.com/role"],
        },
        already_known_entry_id: null,
      },
      {
        proposal: {
          kind: "role",
          label: "AI Engineer",
          aliases: [],
          group: "AI & Data",
          reason: "Already known.",
          source_urls: ["https://example.com/ai"],
        },
        already_known_entry_id: "role-ai-engineer",
      },
    ],
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("SearchVocabularyManager", () => {
  it("shows stable catalog entries and allows explicit lifecycle changes", async () => {
    const user = userEvent.setup();
    render(<SearchVocabularyManager />);

    expect(await screen.findByText("AI Engineer")).toBeInTheDocument();
    expect(screen.getByText("AI & Data")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Deaktivieren" }));
    expect(searchVocabularyApi.update).toHaveBeenCalledWith(
      "role-ai-engineer",
      {
        is_active: false,
      },
    );
  });

  it("creates custom terms without requiring a catalog release", async () => {
    const user = userEvent.setup();
    render(<SearchVocabularyManager />);
    await screen.findByText("AI Engineer");

    await user.type(screen.getByLabelText("Name"), "Agentic Systems Engineer");
    await user.click(
      screen.getByRole("button", { name: "Begriff hinzufügen" }),
    );

    await waitFor(() =>
      expect(searchVocabularyApi.createCustom).toHaveBeenCalledWith(
        expect.objectContaining({
          kind: "role",
          label: "Agentic Systems Engineer",
        }),
      ),
    );
  });

  it("keeps external proposals review-only until one is explicitly accepted", async () => {
    const user = userEvent.setup();
    render(<SearchVocabularyManager />);
    await screen.findByText("AI Engineer");

    await user.click(
      screen.getByRole("button", { name: "Aktualisierungsprompt erzeugen" }),
    );
    expect(
      await screen.findByDisplayValue("RESEARCH CURRENT VOCABULARY"),
    ).toBeInTheDocument();

    await user.type(
      screen.getByLabelText("Katalogvorschläge JSON"),
      JSON.stringify({
        contract: "vocation.search-vocabulary-proposals",
        version: "1.0",
        as_of_date: "2026-08-18",
        proposals: [],
      }),
    );
    await user.click(screen.getByRole("button", { name: "Vorschläge prüfen" }));

    expect(
      await screen.findByText("Agentic Systems Engineer"),
    ).toBeInTheDocument();
    expect(screen.getByText("Bereits vorhanden")).toBeInTheDocument();
    expect(searchVocabularyApi.createCustom).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Übernehmen" }));
    expect(searchVocabularyApi.createCustom).toHaveBeenCalledWith({
      kind: "role",
      label: "Agentic Systems Engineer",
      aliases: ["Agentic AI Engineer"],
      group: "AI & Data",
    });
    expect(await screen.findByText("Übernommen")).toBeInTheDocument();
  });
});
