import { useEffect, useMemo, useState } from "react";

import {
  type CriterionPolicyPayload,
  type CriterionResponse,
  profileApi,
  type SearchProfile,
  type SearchProfilePayload,
} from "./profileApi";

function errorMessage(reason: unknown) {
  return reason instanceof Error
    ? reason.message
    : "Bewertungsregeln konnten nicht verarbeitet werden.";
}

function profilePayload(
  profile: SearchProfile,
  policies: CriterionPolicyPayload[],
): SearchProfilePayload {
  return {
    name: profile.name,
    description: profile.description,
    target_roles: profile.target_roles,
    seniority_targets: profile.seniority_targets ?? [],
    preferred_technologies: profile.preferred_technologies ?? [],
    acceptable_technologies: profile.acceptable_technologies ?? [],
    avoided_technologies: profile.avoided_technologies ?? [],
    target_locations: profile.target_locations ?? [],
    work_models: profile.work_models ?? [],
    relocation_willing: profile.relocation_willing ?? false,
    employment_types: profile.employment_types ?? [],
    preferred_industries: profile.preferred_industries ?? [],
    avoided_industries: profile.avoided_industries ?? [],
    preferred_company_characteristics:
      profile.preferred_company_characteristics ?? [],
    avoided_company_characteristics:
      profile.avoided_company_characteristics ?? [],
    salary_floor: profile.salary_floor ?? null,
    salary_target: profile.salary_target ?? null,
    salary_currency: profile.salary_currency ?? "EUR",
    must_haves: profile.must_haves ?? [],
    must_not_haves: profile.must_not_haves ?? [],
    result_limit: profile.result_limit ?? 12,
    criterion_policies: policies,
  };
}

function blankPolicy(criterion: CriterionResponse): CriterionPolicyPayload {
  return {
    criterion_id: criterion.criterion_id,
    weight: 0,
    required: false,
    numeric_direction: "higher_is_better",
    minimum_numeric_value: null,
    minimum_score: null,
    preferred_boolean: null,
    category_scores: (criterion.allowed_values ?? []).map((value) => ({
      value,
      score: 0,
    })),
  };
}

function policyFor(
  criterion: CriterionResponse,
  policies: CriterionPolicyPayload[],
) {
  return (
    policies.find((item) => item.criterion_id === criterion.criterion_id) ??
    blankPolicy(criterion)
  );
}

function normalizedPolicies(policies: CriterionPolicyPayload[]) {
  return policies.filter(
    (policy) =>
      policy.weight > 0 ||
      policy.required ||
      policy.minimum_numeric_value !== null ||
      policy.minimum_score !== null ||
      policy.preferred_boolean !== null ||
      (policy.category_scores ?? []).some((item) => item.score !== 0),
  );
}

export function EvaluationPolicyPanel() {
  const [profiles, setProfiles] = useState<SearchProfile[]>([]);
  const [criteria, setCriteria] = useState<CriterionResponse[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [policies, setPolicies] = useState<CriterionPolicyPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void Promise.all([
      profileApi.listSearchProfiles(),
      profileApi.listCriteria(),
    ])
      .then(([nextProfiles, nextCriteria]) => {
        setProfiles(nextProfiles);
        setCriteria(
          nextCriteria
            .filter(
              (criterion) =>
                criterion.active &&
                criterion.applicable_subject_type === "opportunity",
            )
            .sort((left, right) => left.display_order - right.display_order),
        );
        const initial =
          nextProfiles.find((profile) => profile.is_default) ?? nextProfiles[0];
        if (initial) {
          setSelectedId(initial.id);
          setPolicies(initial.criterion_policies ?? []);
        }
      })
      .catch((reason) => setError(errorMessage(reason)))
      .finally(() => setLoading(false));
  }, []);

  const selected = useMemo(
    () => profiles.find((profile) => profile.id === selectedId) ?? null,
    [profiles, selectedId],
  );

  function selectProfile(profileId: string) {
    const profile = profiles.find((item) => item.id === profileId);
    setSelectedId(profileId);
    setPolicies(profile?.criterion_policies ?? []);
    setSaved(false);
    setError("");
  }

  function updatePolicy(
    criterion: CriterionResponse,
    patch: Partial<CriterionPolicyPayload>,
  ) {
    setPolicies((current) => {
      const next = [...current];
      const index = next.findIndex(
        (item) => item.criterion_id === criterion.criterion_id,
      );
      const base = index >= 0 ? next[index] : blankPolicy(criterion);
      const updated = { ...base, ...patch };
      if (index >= 0) next[index] = updated;
      else next.push(updated);
      return next;
    });
    setSaved(false);
  }

  async function save() {
    if (!selected) return;
    setSaving(true);
    setSaved(false);
    try {
      const updated = await profileApi.reviseSearchProfile(
        selected.id,
        profilePayload(selected, normalizedPolicies(policies)),
      );
      const nextProfiles = profiles.map((profile) =>
        profile.id === updated.id ? updated : profile,
      );
      setProfiles(nextProfiles);
      setPolicies(updated.criterion_policies ?? []);
      setError("");
      setSaved(true);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="muted">Bewertungsregeln werden geladen…</p>;

  if (profiles.length === 0) {
    return (
      <div className="stack">
        <h2>Bewertung</h2>
        <p className="muted">
          Lege zuerst unter „Suchprofile“ eine Suchstrategie an. Gewichtungen
          gehören immer zu einer konkreten Suchstrategie.
        </p>
      </div>
    );
  }

  return (
    <div className="stack evaluation-policy">
      <div className="section-heading">
        <div>
          <h2>Gewichtung &amp; Bewertungsregeln</h2>
          <p className="muted">
            Gewichtung beeinflusst nur den erklärbaren Fit. Harte Muss- und
            Ausschlussbedingungen bleiben davon getrennt.
          </p>
        </div>
        <label className="compact-control">
          Suchprofil
          <select
            value={selectedId}
            onChange={(event) => selectProfile(event.target.value)}
          >
            {profiles.map((profile) => (
              <option value={profile.id} key={profile.id}>
                {profile.name}
                {profile.is_default ? " · Standard" : ""}
              </option>
            ))}
          </select>
        </label>
      </div>

      {selected && (
        <p className="muted">
          Regeln werden als neue Revision von „{selected.name}“ gespeichert.
          Aktuell Revision {selected.revision}.
        </p>
      )}
      {error && <p className="error-message">{error}</p>}
      {saved && (
        <p className="success-message">Bewertungsregeln gespeichert.</p>
      )}

      {criteria.length === 0 && (
        <p className="muted">Keine aktiven Opportunity-Kriterien vorhanden.</p>
      )}

      <div className="policy-list">
        {criteria.map((criterion) => {
          const policy = policyFor(criterion, policies);
          return (
            <CriterionPolicyCard
              key={criterion.criterion_id}
              criterion={criterion}
              policy={policy}
              onChange={(patch) => updatePolicy(criterion, patch)}
            />
          );
        })}
      </div>

      <div className="actions">
        <button
          className="primary"
          type="button"
          disabled={saving || !selected}
          onClick={() => void save()}
        >
          {saving ? "Speichert…" : "Bewertungsregeln speichern"}
        </button>
      </div>
    </div>
  );
}

function CriterionPolicyCard({
  criterion,
  policy,
  onChange,
}: {
  criterion: CriterionResponse;
  policy: CriterionPolicyPayload;
  onChange: (patch: Partial<CriterionPolicyPayload>) => void;
}) {
  const scoreable = criterion.value_type !== "text";
  return (
    <article className="policy-card">
      <header>
        <div>
          <strong>{criterion.display_name}</strong>
          <p className="muted">{criterion.description}</p>
        </div>
        <span className="badge">{criterion.value_type}</span>
      </header>

      {!scoreable ? (
        <p className="muted">
          Textkriterien werden nicht automatisch in einen numerischen Fit
          umgerechnet. Die Evidenz bleibt im Detail sichtbar.
        </p>
      ) : (
        <>
          <div className="policy-controls">
            <label>
              Gewicht 0–10
              <input
                aria-label={`${criterion.display_name} Gewicht`}
                type="number"
                min="0"
                max="10"
                step="0.5"
                value={policy.weight}
                onChange={(event) =>
                  onChange({ weight: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Mindest-Fit %
              <input
                aria-label={`${criterion.display_name} Mindest-Fit`}
                type="number"
                min="0"
                max="100"
                value={policy.minimum_score ?? ""}
                onChange={(event) =>
                  onChange({
                    minimum_score: event.target.value
                      ? Number(event.target.value)
                      : null,
                  })
                }
              />
            </label>
            <label className="checkbox-label policy-required">
              <input
                type="checkbox"
                checked={policy.required}
                onChange={(event) =>
                  onChange({ required: event.target.checked })
                }
              />
              Harte Schwelle
            </label>
          </div>

          {criterion.value_type === "numeric" && (
            <div className="policy-controls">
              <label>
                Richtung
                <select
                  aria-label={`${criterion.display_name} Richtung`}
                  value={policy.numeric_direction}
                  onChange={(event) =>
                    onChange({
                      numeric_direction: event.target.value as
                        | "higher_is_better"
                        | "lower_is_better",
                    })
                  }
                >
                  <option value="higher_is_better">Höher ist besser</option>
                  <option value="lower_is_better">Niedriger ist besser</option>
                </select>
              </label>
              <label>
                Mindestwert
                <input
                  aria-label={`${criterion.display_name} Mindestwert`}
                  type="number"
                  min={criterion.numeric_min ?? undefined}
                  max={criterion.numeric_max ?? undefined}
                  value={policy.minimum_numeric_value ?? ""}
                  onChange={(event) =>
                    onChange({
                      minimum_numeric_value: event.target.value
                        ? Number(event.target.value)
                        : null,
                    })
                  }
                />
              </label>
              <p className="muted policy-scale">
                Skala {criterion.numeric_min ?? "?"}–
                {criterion.numeric_max ?? "?"}
              </p>
            </div>
          )}

          {criterion.value_type === "boolean" && (
            <label className="compact-control">
              Bevorzugter Wert
              <select
                aria-label={`${criterion.display_name} bevorzugter Wert`}
                value={
                  policy.preferred_boolean === null
                    ? "unset"
                    : String(policy.preferred_boolean)
                }
                onChange={(event) =>
                  onChange({
                    preferred_boolean:
                      event.target.value === "unset"
                        ? null
                        : event.target.value === "true",
                  })
                }
              >
                <option value="unset">Nicht bewerten</option>
                <option value="true">Ja</option>
                <option value="false">Nein</option>
              </select>
            </label>
          )}

          {criterion.value_type === "categorical" && (
            <div className="category-score-grid">
              {(criterion.allowed_values ?? []).map((value) => {
                const configured = (policy.category_scores ?? []).find(
                  (item) => item.value === value,
                );
                return (
                  <label key={value}>
                    {value}
                    <input
                      aria-label={`${criterion.display_name} ${value} Score`}
                      type="number"
                      min="0"
                      max="100"
                      value={configured?.score ?? 0}
                      onChange={(event) => {
                        const scores = [...(policy.category_scores ?? [])];
                        const index = scores.findIndex(
                          (item) => item.value === value,
                        );
                        const next = {
                          value,
                          score: Number(event.target.value),
                        };
                        if (index >= 0) scores[index] = next;
                        else scores.push(next);
                        onChange({ category_scores: scores });
                      }}
                    />
                  </label>
                );
              })}
            </div>
          )}
        </>
      )}
    </article>
  );
}
