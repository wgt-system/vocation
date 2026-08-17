import type { components } from "../../api/generated";
import type { ImportReport } from "../../api/client";

export type GeneratedInitialResearchPrompt =
  components["schemas"]["GeneratedPromptResponse"];
export type InitialPromptPayload = components["schemas"]["InitialPromptPayload"];

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail),
    );
  }
  return response.json() as Promise<T>;
}

export const initialResearchApi = {
  generate: (payload: InitialPromptPayload, includeCandidateProfile: boolean) =>
    request<GeneratedInitialResearchPrompt>(
      `/api/prompts/initial?include_candidate_profile=${includeCandidateProfile ? "true" : "false"}`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),
  importText: (content: string, promptRunId: string) =>
    request<ImportReport>(
      `/api/imports/text?prompt_run_id=${encodeURIComponent(promptRunId)}`,
      {
        method: "POST",
        body: JSON.stringify({ content }),
      },
    ),
};
