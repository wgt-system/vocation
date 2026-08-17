import { type FormEvent, useEffect, useState } from "react";

import {
  profileApi,
  type SearchProfile,
  type SearchProfilePayload,
} from "./profileApi";

type Draft = {
  name: string;
  description: string;
  targetRoles: string;
  seniority: string;
  preferredTech: string;
  acceptableTech: string;
  avoidedTech: string;
  locations: string;
  workModels: SearchProfilePayload["work_models"];
  relocationWilling: boolean;
  employmentTypes: string;
  preferredIndustries: string;
  avoidedIndustries: string;
  preferredCompanies: string;
  avoidedCompanies: string;
  salaryFloor: string;
  salaryTarget: string;
  salaryCurrency: string;
  mustHaves: string;
  mustNotHaves: string;
  resultLimit: string;
};

const blank: Draft = {
  name: "",
  description: "",
  targetRoles: "",
  seniority: "",
  preferredTech: "",
  acceptableTech: "",
  avoidedTech: "",
  locations: "",
  workModels: [],
  relocationWilling: false,
  employmentTypes: "full-time",
  preferredIndustries: "",
  avoidedIndustries: "",
  preferredCompanies: "",
  avoidedCompanies: "",
  salaryFloor: "",
  salaryTarget: "",
  salaryCurrency: "EUR",
  mustHaves: "",
  mustNotHaves: "",
  resultLimit: "12",
};

function lines(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function text(values?: string[] | null) {
  return (values ?? []).join("\n");
}

function errorMessage(reason: unknown) {
  return reason instanceof Error
    ? reason.message
    : "Suchprofil konnte nicht verarbeitet werden.";
}

function toDraft(profile: SearchProfile): Draft {
  return {
    name: profile.name,
    description: profile.description,
    targetRoles: text(profile.target_roles),
    seniority: text(profile.seniority_targets),
    preferredTech: text(profile.preferred_technologies),
    acceptableTech: text(profile.acceptable_technologies),
    avoidedTech: text(profile.avoided_technologies),
    locations: text(profile.target_locations),
    workModels: profile.work_models ?? [],
    relocationWilling: profile.relocation_willing ?? false,
    employmentTypes: text(profile.employment_types),
    preferredIndustries: text(profile.preferred_industries),
    avoidedIndustries: text(profile.avoided_industries),
    preferredCompanies: text(profile.preferred_company_characteristics),
    avoidedCompanies: text(profile.avoided_company_characteristics),
    salaryFloor: profile.salary_floor?.toString() ?? "",
    salaryTarget: profile.salary_target?.toString() ?? "",
    salaryCurrency: profile.salary_currency ?? "EUR",
    mustHaves: text(profile.must_haves),
    mustNotHaves: text(profile.must_not_haves),
    resultLimit: (profile.result_limit ?? 12).toString(),
  };
}

function toPayload(form: Draft): SearchProfilePayload {
  return {
    name: form.name,
    description: form.description,
    target_roles: lines(form.targetRoles),
    seniority_targets: lines(form.seniority),
    preferred_technologies: lines(form.preferredTech),
    acceptable_technologies: lines(form.acceptableTech),
    avoided_technologies: lines(form.avoidedTech),
    target_locations: lines(form.locations),
    work_models: form.workModels ?? [],
    relocation_willing: form.relocationWilling,
    employment_types: lines(form.employmentTypes),
    preferred_industries: lines(form.preferredIndustries),
    avoided_industries: lines(form.avoidedIndustries),
    preferred_company_characteristics: lines(form.preferredCompanies),
    avoided_company_characteristics: lines(form.avoidedCompanies),
    salary_floor: form.salaryFloor ? Number(form.salaryFloor) : null,
    salary_target: form.salaryTarget ? Number(form.salaryTarget) : null,
    salary_currency: form.salaryCurrency || "EUR",
    must_haves: lines(form.mustHaves),
    must_not_haves: lines(form.mustNotHaves),
    result_limit: Number(form.resultLimit || 12),
  };
}

export function SearchProfilesPanel() {
  const [profiles, setProfiles] = useState<SearchProfile[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [form, setForm] = useState<Draft>(blank);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  async function reload(selectId?: string) {
    const next = await profileApi.listSearchProfiles();
    setProfiles(next);
    const targetId = selectId ?? selectedId;
    if (targetId) {
      const selected = next.find((profile) => profile.id === targetId);
      if (selected) {
        setSelectedId(selected.id);
        setForm(toDraft(selected));
      }
    }
  }

  useEffect(() => {
    void profileApi
      .listSearchProfiles()
      .then((next) => {
        setProfiles(next);
        const initial = next.find((item) => item.is_default) ?? next[0];
        if (initial) {
          setSelectedId(initial.id);
          setForm(toDraft(initial));
        }
      })
      .catch((reason) => setError(errorMessage(reason)))
      .finally(() => setLoading(false));
  }, []);

  function select(profile: SearchProfile) {
    setSelectedId(profile.id);
    setForm(toDraft(profile));
    setSaved(false);
    setError("");
  }

  function newProfile() {
    setSelectedId(null);
    setForm(blank);
    setSaved(false);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      const next = selectedId
        ? await profileApi.reviseSearchProfile(selectedId, toPayload(form))
        : await profileApi.createSearchProfile(toPayload(form));
      await reload(next.id);
      setSelectedId(next.id);
      setForm(toDraft(next));
      setError("");
      setSaved(true);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setSaving(false);
    }
  }

  async function makeDefault() {
    if (!selectedId) return;
    try {
      const selected = await profileApi.setDefaultSearchProfile(selectedId);
      await reload(selected.id);
      setError("");
    } catch (reason) {
      setError(errorMessage(reason));
    }
  }

  async function remove() {
    if (!selectedId) return;
    const profile = profiles.find((item) => item.id === selectedId);
    if (
      !window.confirm(`Suchprofil „${profile?.name ?? ""}“ wirklich löschen?`)
    )
      return;
    try {
      await profileApi.deleteSearchProfile(selectedId);
      const next = await profileApi.listSearchProfiles();
      setProfiles(next);
      const initial = next.find((item) => item.is_default) ?? next[0];
      if (initial) {
        setSelectedId(initial.id);
        setForm(toDraft(initial));
      } else {
        setSelectedId(null);
        setForm(blank);
      }
      setError("");
    } catch (reason) {
      setError(errorMessage(reason));
    }
  }

  const selected = profiles.find((item) => item.id === selectedId);

  return (
    <div className="search-profile-layout">
      <aside className="panel stack">
        <div className="section-heading">
          <div>
            <h2>Suchprofile</h2>
            <p className="muted">
              Unterschiedliche Strategien für Rollen, Regionen oder
              Schwerpunkte.
            </p>
          </div>
          <button type="button" onClick={newProfile}>
            + Neu
          </button>
        </div>
        {loading && <p className="muted">Suchprofile werden geladen…</p>}
        {!loading && profiles.length === 0 && (
          <p className="muted">Noch kein Suchprofil angelegt.</p>
        )}
        <div className="group-list">
          {profiles.map((profile) => (
            <button
              className={`group-list-item ${selectedId === profile.id ? "active" : ""}`}
              key={profile.id}
              onClick={() => select(profile)}
              type="button"
            >
              <strong>{profile.name}</strong>
              <small>
                Revision {profile.revision}
                {profile.is_default ? " · Standard" : ""}
              </small>
            </button>
          ))}
        </div>
      </aside>

      <form className="panel stack" onSubmit={submit}>
        <div className="section-heading">
          <div>
            <h2>{selected ? selected.name : "Neues Suchprofil"}</h2>
            <p className="muted">
              {selected
                ? `Revision ${selected.revision}${selected.is_default ? " · aktives Standardprofil" : ""}`
                : "Eine qualitative Jobsuchstrategie anlegen."}
            </p>
          </div>
        </div>

        {error && <p className="error-message">{error}</p>}
        {saved && <p className="success-message">Suchprofil gespeichert.</p>}

        <label>
          Name
          <input
            value={form.name}
            onChange={(event) =>
              setForm((current) => ({ ...current, name: event.target.value }))
            }
            placeholder="z. B. Junior Softwareentwicklung Hamburg"
            required
          />
        </label>
        <label>
          Ziel & Schwerpunkt
          <textarea
            rows={3}
            value={form.description}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
            placeholder="Was soll diese Suche qualitativ finden?"
            required
          />
        </label>

        <div className="profile-form-grid">
          <ListField
            label="Zielrollen"
            value={form.targetRoles}
            placeholder={"Junior Softwareentwickler\nSoftware Engineer"}
            onChange={(targetRoles) =>
              setForm((current) => ({ ...current, targetRoles }))
            }
            required
          />
          <ListField
            label="Seniority"
            value={form.seniority}
            placeholder={"Junior\nEntry Level"}
            onChange={(seniority) =>
              setForm((current) => ({ ...current, seniority }))
            }
          />
          <ListField
            label="Zielorte"
            value={form.locations}
            placeholder={"Hamburg\nBerlin"}
            onChange={(locations) =>
              setForm((current) => ({ ...current, locations }))
            }
          />
          <ListField
            label="Beschäftigungsarten"
            value={form.employmentTypes}
            placeholder="full-time"
            onChange={(employmentTypes) =>
              setForm((current) => ({ ...current, employmentTypes }))
            }
          />
        </div>

        <fieldset className="profile-fieldset">
          <legend>Arbeitsmodell</legend>
          <div className="inline-options">
            <Checkbox
              label="Remote"
              checked={(form.workModels ?? []).includes("remote")}
              onChange={(checked) => setWorkModel("remote", checked, setForm)}
            />
            <Checkbox
              label="Hybrid"
              checked={(form.workModels ?? []).includes("hybrid")}
              onChange={(checked) => setWorkModel("hybrid", checked, setForm)}
            />
            <Checkbox
              label="Vor Ort"
              checked={(form.workModels ?? []).includes("on_site")}
              onChange={(checked) => setWorkModel("on_site", checked, setForm)}
            />
            <Checkbox
              label="Umzug möglich"
              checked={form.relocationWilling}
              onChange={(relocationWilling) =>
                setForm((current) => ({ ...current, relocationWilling }))
              }
            />
          </div>
        </fieldset>

        <div className="profile-form-grid thirds">
          <ListField
            label="Bevorzugte Technologien"
            value={form.preferredTech}
            placeholder={"Java\nC++"}
            onChange={(preferredTech) =>
              setForm((current) => ({ ...current, preferredTech }))
            }
          />
          <ListField
            label="Akzeptable Technologien"
            value={form.acceptableTech}
            placeholder="Python"
            onChange={(acceptableTech) =>
              setForm((current) => ({ ...current, acceptableTech }))
            }
          />
          <ListField
            label="Zu vermeidende Technologien"
            value={form.avoidedTech}
            placeholder="Eine pro Zeile"
            onChange={(avoidedTech) =>
              setForm((current) => ({ ...current, avoidedTech }))
            }
          />
        </div>

        <div className="profile-form-grid">
          <ListField
            label="Bevorzugte Branchen"
            value={form.preferredIndustries}
            onChange={(preferredIndustries) =>
              setForm((current) => ({ ...current, preferredIndustries }))
            }
          />
          <ListField
            label="Zu vermeidende Branchen"
            value={form.avoidedIndustries}
            onChange={(avoidedIndustries) =>
              setForm((current) => ({ ...current, avoidedIndustries }))
            }
          />
          <ListField
            label="Gewünschte Arbeitgebermerkmale"
            value={form.preferredCompanies}
            placeholder={"Gute Einarbeitung\nTechnische Produktentwicklung"}
            onChange={(preferredCompanies) =>
              setForm((current) => ({ ...current, preferredCompanies }))
            }
          />
          <ListField
            label="Unerwünschte Arbeitgebermerkmale"
            value={form.avoidedCompanies}
            onChange={(avoidedCompanies) =>
              setForm((current) => ({ ...current, avoidedCompanies }))
            }
          />
        </div>

        <div className="profile-form-grid salary-grid">
          <label>
            Gehaltsuntergrenze
            <input
              min="0"
              type="number"
              value={form.salaryFloor}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  salaryFloor: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Gehaltsziel
            <input
              min="0"
              type="number"
              value={form.salaryTarget}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  salaryTarget: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Währung
            <input
              maxLength={3}
              value={form.salaryCurrency}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  salaryCurrency: event.target.value.toUpperCase(),
                }))
              }
            />
          </label>
          <label>
            Zielanzahl Ergebnisse
            <input
              min="1"
              max="50"
              type="number"
              value={form.resultLimit}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  resultLimit: event.target.value,
                }))
              }
            />
          </label>
        </div>

        <div className="profile-form-grid">
          <ListField
            label="Muss erfüllt sein"
            value={form.mustHaves}
            placeholder="Eine harte Bedingung pro Zeile"
            onChange={(mustHaves) =>
              setForm((current) => ({ ...current, mustHaves }))
            }
          />
          <ListField
            label="Ausschlusskriterien"
            value={form.mustNotHaves}
            placeholder="Eine harte Ausschlussbedingung pro Zeile"
            onChange={(mustNotHaves) =>
              setForm((current) => ({ ...current, mustNotHaves }))
            }
          />
        </div>

        <div className="actions">
          <button className="primary" type="submit" disabled={saving}>
            {saving
              ? "Speichert…"
              : selected
                ? "Neue Revision speichern"
                : "Suchprofil anlegen"}
          </button>
          {selected && !selected.is_default && (
            <button type="button" onClick={() => void makeDefault()}>
              Als Standard verwenden
            </button>
          )}
          {selected && (
            <button type="button" onClick={() => void remove()}>
              Löschen
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function ListField({
  label,
  value,
  onChange,
  placeholder = "Eine Angabe pro Zeile",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <label>
      {label}
      <textarea
        rows={4}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        required={required}
      />
    </label>
  );
}

function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="checkbox-label">
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      {label}
    </label>
  );
}

function setWorkModel(
  model: NonNullable<SearchProfilePayload["work_models"]>[number],
  checked: boolean,
  setForm: React.Dispatch<React.SetStateAction<Draft>>,
) {
  setForm((current) => {
    const existing = current.workModels ?? [];
    return {
      ...current,
      workModels: checked
        ? [...new Set([...existing, model])]
        : existing.filter((item) => item !== model),
    };
  });
}
