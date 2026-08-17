import type { components } from "../../api/generated";

export type OpportunityFit = components["schemas"]["OpportunityFitResponse"];
export type CriterionContribution =
  components["schemas"]["CriterionContributionResponse"];

async function read<T>(path: string): Promise<T> {
  const response = await fetch(path);
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

export const fitApi = {
  list: (opportunityIds: string[], searchProfileId?: string) => {
    const params = new URLSearchParams();
    if (searchProfileId) params.set("search_profile_id", searchProfileId);
    for (const opportunityId of opportunityIds) {
      params.append("opportunity_id", opportunityId);
    }
    return read<OpportunityFit[]>(`/api/opportunity-fit?${params.toString()}`);
  },
  get: (opportunityId: string, searchProfileId?: string) => {
    const params = new URLSearchParams();
    if (searchProfileId) params.set("search_profile_id", searchProfileId);
    const query = params.size ? `?${params.toString()}` : "";
    return read<OpportunityFit>(
      `/api/opportunities/${encodeURIComponent(opportunityId)}/fit${query}`,
    );
  },
};
