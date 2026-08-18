import type { components } from "../../api/generated";

export type SearchVocabularyEntry =
  components["schemas"]["SearchVocabularyResponse"];
export type CreateSearchVocabularyRequest =
  components["schemas"]["CreateSearchVocabularyRequest"];
export type UpdateSearchVocabularyRequest =
  components["schemas"]["UpdateSearchVocabularyRequest"];
export type SearchVocabularyRefreshPromptRequest =
  components["schemas"]["SearchVocabularyRefreshPromptRequest"];
export type SearchVocabularyRefreshPromptResponse =
  components["schemas"]["SearchVocabularyRefreshPromptResponse"];
export type SearchVocabularyProposalBundle =
  components["schemas"]["SearchVocabularyProposalBundle"];
export type ReviewedSearchVocabularyBundle =
  components["schemas"]["ReviewedSearchVocabularyBundleResponse"];

export type SearchVocabularyKind = SearchVocabularyEntry["kind"];
export type RefreshableSearchVocabularyKind =
  SearchVocabularyRefreshPromptRequest["kinds"][number];

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
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

export const searchVocabularyApi = {
  list: (options?: {
    kind?: SearchVocabularyKind;
    query?: string;
    includeInactive?: boolean;
  }) => {
    const params = new URLSearchParams();
    if (options?.kind) params.set("kind", options.kind);
    if (options?.query) params.set("q", options.query);
    if (options?.includeInactive) params.set("include_inactive", "true");
    const suffix = params.size ? `?${params.toString()}` : "";
    return request<SearchVocabularyEntry[]>(`/api/search-vocabularies${suffix}`);
  },
  createCustom: (payload: CreateSearchVocabularyRequest) =>
    request<SearchVocabularyEntry>("/api/search-vocabularies/custom", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  update: (id: string, payload: UpdateSearchVocabularyRequest) =>
    request<SearchVocabularyEntry>(
      `/api/search-vocabularies/${encodeURIComponent(id)}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
    ),
  generateRefreshPrompt: (payload: SearchVocabularyRefreshPromptRequest) =>
    request<SearchVocabularyRefreshPromptResponse>(
      "/api/search-vocabularies/refresh-prompt",
      { method: "POST", body: JSON.stringify(payload) },
    ),
  reviewProposals: (payload: SearchVocabularyProposalBundle) =>
    request<ReviewedSearchVocabularyBundle>(
      "/api/search-vocabularies/proposals/review",
      { method: "POST", body: JSON.stringify(payload) },
    ),
};
