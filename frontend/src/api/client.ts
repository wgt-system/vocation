import type { components } from "./generated";

export type Criterion = components["schemas"]["CriterionResponse"];
export type ImportIssue = components["schemas"]["ImportIssueResponse"];
export type ImportReport = components["schemas"]["ImportReportResponse"];
export type OpportunityListItem =
  components["schemas"]["OpportunityListItemResponse"];
export type OpportunityDetail =
  components["schemas"]["OpportunityDetailResponse"];

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

export const api = {
  listCriteria: () => request<Criterion[]>("/api/criteria"),
  createCriterion: (
    criterion: Omit<components["schemas"]["CriterionPayload"], "revision">,
  ) =>
    request<Criterion>("/api/criteria", {
      method: "POST",
      body: JSON.stringify(criterion),
    }),
  editCriterion: (
    criterion: Omit<components["schemas"]["CriterionPayload"], "revision">,
  ) =>
    request<Criterion>(`/api/criteria/${criterion.criterion_id}`, {
      method: "PUT",
      body: JSON.stringify(criterion),
    }),
  activateCriterion: (criterionId: string, active: boolean) =>
    request<Criterion>(`/api/criteria/${criterionId}/activation`, {
      method: "POST",
      body: JSON.stringify({ active }),
    }),
  reorderCriteria: (criterionIds: string[]) =>
    request<Criterion[]>("/api/criteria/reorder", {
      method: "POST",
      body: JSON.stringify({ criterion_ids: criterionIds }),
    }),
  generatePrompt: (payload: components["schemas"]["InitialPromptPayload"]) =>
    request<components["schemas"]["GeneratedPromptResponse"]>(
      "/api/prompts/initial",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),
  importText: (content: string) =>
    request<ImportReport>("/api/imports/text", {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  getImportReport: (id: string) => request<ImportReport>(`/api/imports/${id}`),
  listOpportunities: () => request<OpportunityListItem[]>("/api/opportunities"),
  getOpportunity: (id: string) =>
    request<OpportunityDetail>(`/api/opportunities/${id}`),
};
