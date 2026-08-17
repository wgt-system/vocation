import type { components } from "../../api/generated";

export type CandidateProfile =
  components["schemas"]["CandidateProfileResponse"];
export type CandidateProfilePayload =
  components["schemas"]["CandidateProfilePayload"];
export type EducationPayload = components["schemas"]["EducationPayload"];
export type SkillPayload = components["schemas"]["SkillPayload"];
export type LanguagePayload = components["schemas"]["LanguagePayload"];
export type ProjectHighlightPayload =
  components["schemas"]["ProjectHighlightPayload"];
export type SearchProfile = components["schemas"]["SearchProfileResponse"];
export type SearchProfilePayload =
  components["schemas"]["SearchProfilePayload"];

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
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const profileApi = {
  getCandidate: () =>
    request<CandidateProfile | null>("/api/profiles/candidate"),
  saveCandidate: (payload: CandidateProfilePayload) =>
    request<CandidateProfile>("/api/profiles/candidate", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  listSearchProfiles: () => request<SearchProfile[]>("/api/profiles/search"),
  createSearchProfile: (payload: SearchProfilePayload) =>
    request<SearchProfile>("/api/profiles/search", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  reviseSearchProfile: (id: string, payload: SearchProfilePayload) =>
    request<SearchProfile>(`/api/profiles/search/${encodeURIComponent(id)}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  setDefaultSearchProfile: (id: string) =>
    request<SearchProfile>(
      `/api/profiles/search/${encodeURIComponent(id)}/default`,
      { method: "POST" },
    ),
  deleteSearchProfile: (id: string) =>
    request<void>(`/api/profiles/search/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
};
