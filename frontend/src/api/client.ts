import type { components } from "./generated";

export type Criterion = components["schemas"]["CriterionResponse"];
export type ImportIssue = components["schemas"]["ImportIssueResponse"];
export type ImportReport = components["schemas"]["ImportReportResponse"];
export type UpdateMode = components["schemas"]["UpdatePromptPayload"]["mode"];
export type UpdatePromptOptions =
  components["schemas"]["UpdatePromptOptionsResponse"];
export type GeneratedUpdatePrompt =
  components["schemas"]["GeneratedUpdatePromptResponse"];
export type GapRequest = components["schemas"]["GapRequestPayload"];
export type AvailabilityPrompt =
  components["schemas"]["AvailabilityPromptPayload"];
export type GeneratedAvailabilityPrompt =
  components["schemas"]["GeneratedAvailabilityPromptResponse"];
export type AvailabilityImportReport =
  components["schemas"]["AvailabilityImportReportResponse"];
export type TrackingStatus =
  components["schemas"]["OpportunityListItemResponse"]["tracking_status"];
export type OpportunityListItem =
  components["schemas"]["OpportunityListItemResponse"];
export type OpportunityDetail =
  components["schemas"]["OpportunityDetailResponse"];
export type OpportunityGroup =
  components["schemas"]["OpportunityGroupResponse"];
export type OpportunityGroupSummary =
  components["schemas"]["OpportunityGroupSummaryResponse"];
export type OpportunityGroupPayload =
  components["schemas"]["OpportunityGroupPayload"];
export type OpportunityGroupMembershipPayload =
  components["schemas"]["OpportunityGroupMembershipPayload"];
export type OpportunityGroupReorderPayload =
  components["schemas"]["OpportunityGroupReorderPayload"];
export type MapLocation = components["schemas"]["MapLocationResponse"];
export type MapResolution = components["schemas"]["MapResolutionResponse"];
export type MapResolutionPayload =
  components["schemas"]["MapResolutionPayload"];
export type GeocodeResolutionPayload =
  components["schemas"]["GeocodeResolutionPayload"];
export type MapProjectionFeature =
  components["schemas"]["MapProjectionFeatureResponse"];
export type ExternalLink = components["schemas"]["ExternalLinkResponse"];
export type ExternalLinkOpenPayload =
  components["schemas"]["ExternalLinkOpenPayload"];
export type OpportunityComparison =
  components["schemas"]["OpportunityComparisonResponse"];
export type ComparisonOpportunity =
  components["schemas"]["ComparisonOpportunityResponse"];
export type ApplicationLifecycle =
  components["schemas"]["ApplicationCaseResponse"]["lifecycle"];
export type ApplicationCase = components["schemas"]["ApplicationCaseResponse"];
export type ApplicationLifecycleEvent =
  components["schemas"]["ApplicationLifecycleEventResponse"];
export type ApplicationMaterial =
  components["schemas"]["ApplicationMaterialResponse"];
export type ApplicationMaterialKind =
  components["schemas"]["ApplicationMaterialResponse"]["kind"];
export type ApplicationDocument =
  components["schemas"]["ApplicationDocumentResponse"];
export type DuplicateCaseReview =
  components["schemas"]["DuplicateCaseReviewResponse"];
export type DuplicateDecisionPayload =
  components["schemas"]["DuplicateDecisionPayload"];
export type DuplicateDecisionOutcome = DuplicateDecisionPayload["outcome"];

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isMultipart = init?.body instanceof FormData;
  const response = await fetch(path, {
    ...init,
    headers: isMultipart
      ? init?.headers
      : { "Content-Type": "application/json", ...init?.headers },
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
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function requestNotFoundAsNull<T>(path: string): Promise<T | null> {
  const response = await fetch(path);
  if (response.status === 404) return null;
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
  getUpdatePromptOptions: () =>
    request<UpdatePromptOptions>("/api/prompts/update-options"),
  generateUpdatePrompt: (
    payload: components["schemas"]["UpdatePromptPayload"],
  ) =>
    request<GeneratedUpdatePrompt>("/api/prompts/update", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  generateAvailabilityPrompt: (payload: AvailabilityPrompt) =>
    request<GeneratedAvailabilityPrompt>("/api/prompts/availability-check", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  importText: (content: string) =>
    request<ImportReport>("/api/imports/text", {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  importAvailabilityText: (content: string) =>
    request<AvailabilityImportReport>("/api/availability/imports/text", {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  getImportReport: (id: string) => request<ImportReport>(`/api/imports/${id}`),
  listOpportunities: (groupId?: string) =>
    request<OpportunityListItem[]>(
      groupId
        ? `/api/opportunities?group_id=${encodeURIComponent(groupId)}`
        : "/api/opportunities",
    ),
  getOpportunity: (id: string) =>
    request<OpportunityDetail>(`/api/opportunities/${id}`),
  listApplicationCases: (opportunityId: string) =>
    request<ApplicationCase[]>(
      `/api/opportunities/${opportunityId}/application-cases`,
    ),
  createApplicationCase: (opportunityId: string) =>
    request<ApplicationCase>(
      `/api/opportunities/${opportunityId}/application-cases`,
      { method: "POST" },
    ),
  getApplicationCase: (caseId: string) =>
    request<ApplicationCase>(`/api/application-cases/${caseId}`),
  changeApplicationCaseLifecycle: (
    caseId: string,
    lifecycle: ApplicationLifecycle,
  ) =>
    request<ApplicationCase>(`/api/application-cases/${caseId}/lifecycle`, {
      method: "POST",
      body: JSON.stringify({ lifecycle }),
    }),
  listApplicationMaterials: (caseId: string) =>
    request<ApplicationMaterial[]>(
      `/api/application-cases/${caseId}/materials`,
    ),
  createApplicationMaterial: (
    caseId: string,
    kind: ApplicationMaterialKind,
    displayName: string,
  ) =>
    request<ApplicationMaterial>(`/api/application-cases/${caseId}/materials`, {
      method: "POST",
      body: JSON.stringify({ kind, display_name: displayName }),
    }),
  reviseApplicationMaterial: (materialId: string, displayName: string) =>
    request<ApplicationMaterial>(
      `/api/application-materials/${materialId}/revisions`,
      { method: "POST", body: JSON.stringify({ display_name: displayName }) },
    ),
  getApplicationDocumentForMaterialRevision: (
    materialId: string,
    revision: number,
  ) =>
    requestNotFoundAsNull<ApplicationDocument>(
      `/api/application-materials/${materialId}/revisions/${revision}/document`,
    ),
  attachApplicationDocument: (
    materialId: string,
    revision: number,
    file: File,
  ) => {
    const form = new FormData();
    form.append("file", file);
    return request<ApplicationDocument>(
      `/api/application-materials/${materialId}/revisions/${revision}/document`,
      { method: "POST", body: form },
    );
  },
  getApplicationDocument: (documentId: string) =>
    request<ApplicationDocument>(`/api/application-documents/${documentId}`),
  listDuplicateCases: () =>
    request<DuplicateCaseReview[]>("/api/duplicate-cases"),
  getDuplicateCase: (caseId: string) =>
    request<DuplicateCaseReview>(
      `/api/duplicate-cases/${encodeURIComponent(caseId)}`,
    ),
  decideDuplicateCase: (caseId: string, payload: DuplicateDecisionPayload) =>
    request<DuplicateCaseReview>(
      `/api/duplicate-cases/${encodeURIComponent(caseId)}/decisions`,
      { method: "POST", body: JSON.stringify(payload) },
    ),
  listExternalLinks: (opportunityId: string) =>
    request<ExternalLink[]>(
      `/api/external-links/opportunities/${opportunityId}`,
    ),
  openExternalLink: (opportunityId: string, postingId?: string) =>
    request<ExternalLink>(
      `/api/external-links/opportunities/${opportunityId}/open`,
      {
        method: "POST",
        body: JSON.stringify(
          postingId === undefined ? {} : { posting_id: postingId },
        ),
      },
    ),
  compareOpportunities: (opportunityIds: string[]) =>
    request<OpportunityComparison>("/api/comparison/opportunities", {
      method: "POST",
      body: JSON.stringify({ opportunity_ids: opportunityIds }),
    }),
  listGroups: () => request<OpportunityGroup[]>("/api/groups"),
  getGroup: (id: string) => request<OpportunityGroup>(`/api/groups/${id}`),
  createGroup: (payload: OpportunityGroupPayload) =>
    request<OpportunityGroup>("/api/groups", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  editGroup: (id: string, payload: OpportunityGroupPayload) =>
    request<OpportunityGroup>(`/api/groups/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteGroup: (id: string) =>
    request<void>(`/api/groups/${id}`, { method: "DELETE" }),
  addGroupMembership: (groupId: string, opportunityId: string) =>
    request<OpportunityGroup>(`/api/groups/${groupId}/memberships`, {
      method: "POST",
      body: JSON.stringify({ opportunity_id: opportunityId }),
    }),
  removeGroupMembership: (groupId: string, opportunityId: string) =>
    request<OpportunityGroup>(
      `/api/groups/${groupId}/memberships/${opportunityId}`,
      { method: "DELETE" },
    ),
  reorderGroup: (groupId: string, opportunityIds: string[]) =>
    request<OpportunityGroup>(`/api/groups/${groupId}/order`, {
      method: "PUT",
      body: JSON.stringify({ opportunity_ids: opportunityIds }),
    }),
  listMapLocations: () => request<MapLocation[]>("/api/map/locations"),
  setMapResolution: (workLocationId: string, payload: MapResolutionPayload) =>
    request<MapResolution>(`/api/map/locations/${workLocationId}/resolution`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteMapResolution: (workLocationId: string) =>
    request<void>(`/api/map/locations/${workLocationId}/resolution`, {
      method: "DELETE",
    }),
  geocodeMapLocation: (
    workLocationId: string,
    payload: GeocodeResolutionPayload,
  ) =>
    request<MapResolution>(`/api/map/locations/${workLocationId}/geocode`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getMapProjection: (opportunityIds: string[]) =>
    request<MapProjectionFeature[]>("/api/map/projection", {
      method: "POST",
      body: JSON.stringify({ opportunity_ids: opportunityIds }),
    }),
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
      {
        method: "POST",
        body: JSON.stringify({
          ...(target_status === undefined ? {} : { target_status }),
          ...(reason === undefined ? {} : { reason }),
        }),
      },
    ),
};
