export type OpportunityNote = {
  opportunity_id: string;
  content: string;
  updated_at: string;
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

export const opportunityNoteApi = {
  get: (opportunityId: string) =>
    request<OpportunityNote | null>(
      `/api/opportunities/${encodeURIComponent(opportunityId)}/note`,
    ),
  save: (opportunityId: string, content: string) =>
    request<OpportunityNote | null>(
      `/api/opportunities/${encodeURIComponent(opportunityId)}/note`,
      {
        method: "PUT",
        body: JSON.stringify({ content }),
      },
    ),
};
