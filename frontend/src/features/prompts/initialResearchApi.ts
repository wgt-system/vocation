import type { ImportReport } from "../../api/client";
import type { components } from "../../api/generated";

export type GeneratedInitialResearchPrompt =
  components["schemas"]["GeneratedPromptResponse"] & {
    prompt_context_ref?: string;
  };
export type InitialPromptPayload =
  components["schemas"]["InitialPromptPayload"];

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

async function generate(
  payload: InitialPromptPayload,
  includeCandidateProfile: boolean,
): Promise<GeneratedInitialResearchPrompt> {
  const response = await fetch(
    `/api/prompts/initial?include_candidate_profile=${includeCandidateProfile ? "true" : "false"}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
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
  const promptContextRef = response.headers.get("X-Prompt-Context-Ref");
  if (!promptContextRef) {
    throw new Error("Initial Research response is missing prompt context provenance.");
  }
  const body = (await response.json()) as components["schemas"]["GeneratedPromptResponse"];
  return { ...body, prompt_context_ref: promptContextRef };
}

export const initialResearchApi = {
  generate,
  importText: (content: string, promptRunId: string) =>
    request<ImportReport>(
      `/api/imports/text?prompt_run_id=${encodeURIComponent(promptRunId)}`,
      {
        method: "POST",
        body: JSON.stringify({ content }),
      },
    ),
};
