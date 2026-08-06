export type Criterion = {
  criterion_id: string;
  display_name: string;
  description: string;
  value_type: "numeric" | "boolean" | "categorical" | "text";
  numeric_min: number | null;
  numeric_max: number | null;
  allowed_values: string[];
  applicable_subject_type: "company" | "opportunity" | "posting";
  active: boolean;
  display_order: number;
  revision: number;
};

export type ImportIssue = { severity: string; code: string; path: string; message: string };
export type ImportReport = {
  import_id: string;
  status: "applied" | "rejected" | "duplicate";
  bundle_id: string | null;
  fingerprint: string | null;
  counts: Record<string, number>;
  warnings: string[];
  issues: ImportIssue[];
  duplicate_of_import_id: string | null;
};

export type OpportunityListItem = {
  id: string;
  title: string;
  company_name: string;
  locations: string[];
  posting_count: number;
  assessment_count: number;
  import_id: string;
  imported_at: string;
};

export type OpportunityDetail = {
  id: string;
  title: string;
  company: { id: string; name: string };
  locations: Array<{ label: string; precision: string; evidence_summary: string | null }>;
  postings: Array<{
    id: string;
    title: string;
    published_at: string | null;
    observed_at: string;
    source: { id: string; name: string; type: string };
    source_reference: { id: string; url: string; display_label: string | null; observed_at: string };
  }>;
  sources: Array<{ id: string; name: string; type: string; base_url: string | null }>;
  observations: Array<{
    id: string;
    subject_type: string;
    type: string;
    value: unknown;
    observed_at: string;
    confidence: number | null;
    evidence_summary: string | null;
  }>;
  assessments: Array<{
    id: string;
    criterion_id: string;
    criterion_name: string;
    value: unknown;
    origin: string;
    reasoning: string | null;
  }>;
  import_provenance: { import_id: string; bundle_id: string; fingerprint: string; applied_at: string };
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail));
  }
  return response.json() as Promise<T>;
}

export const api = {
  listCriteria: () => request<Criterion[]>("/api/criteria"),
  createCriterion: (criterion: Omit<Criterion, "revision">) =>
    request<Criterion>("/api/criteria", { method: "POST", body: JSON.stringify(criterion) }),
  editCriterion: (criterion: Omit<Criterion, "revision">) =>
    request<Criterion>(`/api/criteria/${criterion.criterion_id}`, { method: "PUT", body: JSON.stringify(criterion) }),
  activateCriterion: (criterionId: string, active: boolean) =>
    request<Criterion>(`/api/criteria/${criterionId}/activation`, {
      method: "POST",
      body: JSON.stringify({ active })
    }),
  reorderCriteria: (criterionIds: string[]) =>
    request<Criterion[]>("/api/criteria/reorder", { method: "POST", body: JSON.stringify({ criterion_ids: criterionIds }) }),
  generatePrompt: (payload: { search_profile: string; constraints: string[]; as_of_date: string }) =>
    request<{ prompt_run_id: string; prompt_text: string; bundle_version: string; criteria_count: number }>(
      "/api/prompts/initial",
      { method: "POST", body: JSON.stringify(payload) }
    ),
  importText: (content: string) =>
    request<ImportReport>("/api/imports/text", { method: "POST", body: JSON.stringify({ content }) }),
  getImportReport: (id: string) => request<ImportReport>(`/api/imports/${id}`),
  listOpportunities: () => request<OpportunityListItem[]>("/api/opportunities"),
  getOpportunity: (id: string) => request<OpportunityDetail>(`/api/opportunities/${id}`)
};
