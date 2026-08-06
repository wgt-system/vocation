import type { components } from "./generated";

export type Criterion = components["schemas"]["CriterionResponse"];
export type ImportIssue = components["schemas"]["ImportIssueResponse"];
export type ImportReport = components["schemas"]["ImportReportResponse"];
export type TrackingStatus =
  | "new"
  | "to_review"
  | "interesting"
  | "shortlisted"
  | "deferred"
  | "excluded"
  | "archived";
export type OpportunityListItem = Omit<
  components["schemas"]["OpportunityListItemResponse"],
  "tracking_status"
> & { tracking_status?: TrackingStatus };
export type OpportunityDetail = Omit<
  components["schemas"]["OpportunityDetailResponse"],
  | "tracking_status"
  | "external_assessments"
  | "personal_assessments"
  | "personal_assessment_history"
  | "decision_history"
> & {
  tracking_status?: TrackingStatus;
  external_assessments?: components["schemas"]["AssessmentResponse"][];
  personal_assessments?: components["schemas"]["PersonalAssessmentResponse"][];
  personal_assessment_history?: components["schemas"]["PersonalAssessmentResponse"][];
  decision_history?: components["schemas"]["DecisionResponse"][];
};

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
  createPersonalAssessment: (
    id: string,
    payload: components["schemas"]["PersonalAssessmentPayload"],
  ) =>
    request<components["schemas"]["PersonalAssessmentResponse"]>(
      `/api/opportunities/${id}/assessments/personal`,
      { method: "POST", body: JSON.stringify(payload) },
    ),
  revisePersonalAssessment: (
    id: string,
    assessmentId: string,
    payload: components["schemas"]["PersonalAssessmentRevisionPayload"],
  ) =>
    request<components["schemas"]["PersonalAssessmentResponse"]>(
      `/api/opportunities/${id}/assessments/personal/${assessmentId}/revisions`,
      { method: "POST", body: JSON.stringify(payload) },
    ),
  changeStatus: (id: string, status: TrackingStatus, reason?: string) =>
    request<components["schemas"]["DecisionResponse"]>(
      `/api/opportunities/${id}/status`,
      { method: "POST", body: JSON.stringify({ status, reason }) },
    ),
  exclude: (id: string, reason: string) =>
    request<components["schemas"]["DecisionResponse"]>(
      `/api/opportunities/${id}/exclude`,
      { method: "POST", body: JSON.stringify({ reason }) },
    ),
  restore: (id: string, target_status?: TrackingStatus, reason?: string) =>
    request<components["schemas"]["DecisionResponse"]>(
      `/api/opportunities/${id}/restore`,
      { method: "POST", body: JSON.stringify({ target_status, reason }) },
    ),
};
