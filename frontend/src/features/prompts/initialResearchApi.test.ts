import { afterEach, describe, expect, it, vi } from "vitest";

import { initialResearchApi } from "./initialResearchApi";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("initialResearchApi", () => {
  it("exposes prompt context provenance from the initial prompt response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          prompt_run_id: "run-1",
          prompt_text: "prompt",
          bundle_version: "1.0",
          criteria_count: 3,
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "X-Prompt-Context-Ref": "ctx-1",
          },
        },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await initialResearchApi.generate(
      {
        search_profile: "search-1",
        constraints: [],
        as_of_date: "2026-08-18",
      },
      true,
    );

    expect(result.prompt_context_ref).toBe("ctx-1");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/prompts/initial?include_candidate_profile=true",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("rejects an initial prompt response without provenance", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            prompt_run_id: "run-1",
            prompt_text: "prompt",
            bundle_version: "1.0",
            criteria_count: 3,
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    await expect(
      initialResearchApi.generate(
        {
          search_profile: "search-1",
          constraints: [],
          as_of_date: "2026-08-18",
        },
        false,
      ),
    ).rejects.toThrow("missing prompt context provenance");
  });
});
