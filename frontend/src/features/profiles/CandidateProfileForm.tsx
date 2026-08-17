import { type FormEvent, useEffect, useState } from "react";

import {
  type CandidateProfile,
  type CandidateProfilePayload,
  type EducationPayload,
  type LanguagePayload,
  profileApi,
  type ProjectHighlightPayload,
  type SkillPayload,
} from "./profileApi";

const emptyEducation: EducationPayload = {
  degree: "",
  field: "",
  institution: "",
  status: "completed",
  graduation_year: null,
};

const emptySkill: SkillPayload = {
  name: "",
  level: "working",
  notes: null,
};

const emptyLanguage: LanguagePayload = { name: "", level: "" };
const emptyProject: ProjectHighlightPayload = {
  name: "",
  summary: "",
  technologies: [],
};

const emptyCandidate: CandidateProfilePayload = {
  headline: "",
  summary: "",
  education: [],
  skills: [],
  languages: [],
  experience_summary: "",
  projects: [],
  interests: [],
};

function lines(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function errorMessage(reason: unknown) {
  return reason instanceof Error
    ? reason.message
    : "Profil konnte nicht gespeichert werden.";
}

export function CandidateProfileForm() {
  const [form, setForm] = useState<CandidateProfilePayload>(emptyCandidate);
  const [revision, setRevision] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    void profileApi
      .getCandidate()
      .then((profile) => {
        if (profile) {
          setRevision(profile.revision);
          setForm(toPayload(profile));
        }
      })
      .catch((reason) => setError(errorMessage(reason)))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      const next = await profileApi.saveCandidate(form);
      setRevision(next.revision);
      setForm(toPayload(next));
      setError("");
      setSaved(true);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="muted">Profil wird geladen…</p>;

  return (
    <form className="stack" onSubmit={submit}>
      <div className="section-heading">
        <div>
          <h2>Mein Profil</h2>
          <p className="muted">
            Private Qualifikationsfakten für Recherche und spätere Fit-Analyse.
            {revision ? ` Aktuelle Revision: ${revision}.` : ""}
          </p>
        </div>
      </div>

      {error && <p className="error-message">{error}</p>}
      {saved && <p className="success-message">Profil gespeichert.</p>}

      <label>
        Profilüberschrift
        <input
          value={form.headline}
          onChange={(event) =>
            setForm((current) => ({ ...current, headline: event.target.value }))
          }
          placeholder="z. B. Junior Softwareentwickler mit Informatik-Hintergrund"
          required
        />
      </label>

      <label>
        Kurzprofil
        <textarea
          rows={4}
          value={form.summary}
          onChange={(event) =>
            setForm((current) => ({ ...current, summary: event.target.value }))
          }
          placeholder="Was zeichnet dein fachliches Profil aus?"
          required
        />
      </label>

      <label>
        Erfahrung
        <textarea
          rows={4}
          value={form.experience_summary ?? ""}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              experience_summary: event.target.value,
            }))
          }
          placeholder="Berufliche, Studien- und Projekterfahrung, die für Stellen relevant ist."
        />
      </label>

      <EditableSection
        title="Abschlüsse & Ausbildung"
        onAdd={() =>
          setForm((current) => ({
            ...current,
            education: [...(current.education ?? []), { ...emptyEducation }],
          }))
        }
      >
        {(form.education ?? []).map((item, index) => (
          <div
            className="profile-row profile-row-wide"
            key={`education-${index}`}
          >
            <input
              aria-label={`Abschluss ${index + 1}`}
              placeholder="Abschluss"
              value={item.degree}
              onChange={(event) =>
                updateEducation(
                  index,
                  { degree: event.target.value },
                  form,
                  setForm,
                )
              }
            />
            <input
              aria-label={`Fach ${index + 1}`}
              placeholder="Fach"
              value={item.field}
              onChange={(event) =>
                updateEducation(
                  index,
                  { field: event.target.value },
                  form,
                  setForm,
                )
              }
            />
            <input
              aria-label={`Institution ${index + 1}`}
              placeholder="Institution"
              value={item.institution}
              onChange={(event) =>
                updateEducation(
                  index,
                  { institution: event.target.value },
                  form,
                  setForm,
                )
              }
            />
            <input
              aria-label={`Jahr ${index + 1}`}
              type="number"
              placeholder="Jahr"
              value={item.graduation_year ?? ""}
              onChange={(event) =>
                updateEducation(
                  index,
                  {
                    graduation_year: event.target.value
                      ? Number(event.target.value)
                      : null,
                  },
                  form,
                  setForm,
                )
              }
            />
            <button
              type="button"
              onClick={() =>
                setForm((current) => ({
                  ...current,
                  education: (current.education ?? []).filter(
                    (_, itemIndex) => itemIndex !== index,
                  ),
                }))
              }
            >
              Entfernen
            </button>
          </div>
        ))}
      </EditableSection>

      <EditableSection
        title="Skills & Technologien"
        onAdd={() =>
          setForm((current) => ({
            ...current,
            skills: [...(current.skills ?? []), { ...emptySkill }],
          }))
        }
      >
        {(form.skills ?? []).map((item, index) => (
          <div className="profile-row" key={`skill-${index}`}>
            <input
              aria-label={`Skill ${index + 1}`}
              placeholder="Skill / Technologie"
              value={item.name}
              onChange={(event) =>
                updateArrayItem(
                  "skills",
                  index,
                  { ...item, name: event.target.value },
                  setForm,
                )
              }
            />
            <select
              aria-label={`Skill-Level ${index + 1}`}
              value={item.level}
              onChange={(event) =>
                updateArrayItem(
                  "skills",
                  index,
                  {
                    ...item,
                    level: event.target.value as SkillPayload["level"],
                  },
                  setForm,
                )
              }
            >
              <option value="learning">Lerne ich</option>
              <option value="basic">Grundlagen</option>
              <option value="working">Arbeitssicher</option>
              <option value="strong">Stark</option>
              <option value="expert">Experte</option>
            </select>
            <input
              aria-label={`Skill-Notiz ${index + 1}`}
              placeholder="Kontext / Notiz"
              value={item.notes ?? ""}
              onChange={(event) =>
                updateArrayItem(
                  "skills",
                  index,
                  { ...item, notes: event.target.value || null },
                  setForm,
                )
              }
            />
            <RemoveButton
              onClick={() => removeArrayItem("skills", index, setForm)}
            />
          </div>
        ))}
      </EditableSection>

      <EditableSection
        title="Sprachen"
        onAdd={() =>
          setForm((current) => ({
            ...current,
            languages: [...(current.languages ?? []), { ...emptyLanguage }],
          }))
        }
      >
        {(form.languages ?? []).map((item, index) => (
          <div className="profile-row compact" key={`language-${index}`}>
            <input
              aria-label={`Sprache ${index + 1}`}
              placeholder="Sprache"
              value={item.name}
              onChange={(event) =>
                updateArrayItem(
                  "languages",
                  index,
                  { ...item, name: event.target.value },
                  setForm,
                )
              }
            />
            <input
              aria-label={`Sprachniveau ${index + 1}`}
              placeholder="Niveau"
              value={item.level}
              onChange={(event) =>
                updateArrayItem(
                  "languages",
                  index,
                  { ...item, level: event.target.value },
                  setForm,
                )
              }
            />
            <RemoveButton
              onClick={() => removeArrayItem("languages", index, setForm)}
            />
          </div>
        ))}
      </EditableSection>

      <EditableSection
        title="Projekte & Portfolio"
        onAdd={() =>
          setForm((current) => ({
            ...current,
            projects: [...(current.projects ?? []), { ...emptyProject }],
          }))
        }
      >
        {(form.projects ?? []).map((item, index) => (
          <div className="profile-card" key={`project-${index}`}>
            <div className="profile-row compact">
              <input
                aria-label={`Projekt ${index + 1}`}
                placeholder="Projektname"
                value={item.name}
                onChange={(event) =>
                  updateArrayItem(
                    "projects",
                    index,
                    { ...item, name: event.target.value },
                    setForm,
                  )
                }
              />
              <RemoveButton
                onClick={() => removeArrayItem("projects", index, setForm)}
              />
            </div>
            <textarea
              aria-label={`Projektbeschreibung ${index + 1}`}
              rows={2}
              placeholder="Kurzbeschreibung"
              value={item.summary}
              onChange={(event) =>
                updateArrayItem(
                  "projects",
                  index,
                  { ...item, summary: event.target.value },
                  setForm,
                )
              }
            />
            <input
              aria-label={`Projekttechnologien ${index + 1}`}
              placeholder="Technologien, durch Kommas getrennt"
              value={(item.technologies ?? []).join(", ")}
              onChange={(event) =>
                updateArrayItem(
                  "projects",
                  index,
                  {
                    ...item,
                    technologies: event.target.value
                      .split(",")
                      .map((value) => value.trim())
                      .filter(Boolean),
                  },
                  setForm,
                )
              }
            />
          </div>
        ))}
      </EditableSection>

      <label>
        Interessen
        <textarea
          rows={4}
          value={(form.interests ?? []).join("\n")}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              interests: lines(event.target.value),
            }))
          }
          placeholder={
            "Ein Interesse pro Zeile\nOpen Source\nSoftwarearchitektur"
          }
        />
      </label>

      <div className="actions">
        <button className="primary" type="submit" disabled={saving}>
          {saving
            ? "Speichert…"
            : revision
              ? "Neue Revision speichern"
              : "Profil speichern"}
        </button>
      </div>
    </form>
  );
}

function toPayload(profile: CandidateProfile): CandidateProfilePayload {
  const { revision: _revision, ...payload } = profile;
  return payload;
}

type ArrayKey = "skills" | "languages" | "projects";

function updateArrayItem(
  key: ArrayKey,
  index: number,
  value: SkillPayload | LanguagePayload | ProjectHighlightPayload,
  setForm: React.Dispatch<React.SetStateAction<CandidateProfilePayload>>,
) {
  setForm((current) => {
    const next = [...((current[key] ?? []) as (typeof value)[])];
    next[index] = value;
    return { ...current, [key]: next };
  });
}

function removeArrayItem(
  key: ArrayKey,
  index: number,
  setForm: React.Dispatch<React.SetStateAction<CandidateProfilePayload>>,
) {
  setForm((current) => ({
    ...current,
    [key]: (current[key] ?? []).filter((_, itemIndex) => itemIndex !== index),
  }));
}

function updateEducation(
  index: number,
  patch: Partial<EducationPayload>,
  form: CandidateProfilePayload,
  setForm: React.Dispatch<React.SetStateAction<CandidateProfilePayload>>,
) {
  const next = [...(form.education ?? [])];
  next[index] = { ...next[index], ...patch };
  setForm((current) => ({ ...current, education: next }));
}

function EditableSection({
  title,
  onAdd,
  children,
}: {
  title: string;
  onAdd: () => void;
  children: React.ReactNode;
}) {
  return (
    <fieldset className="profile-fieldset">
      <legend>{title}</legend>
      <div className="stack">{children}</div>
      <button type="button" onClick={onAdd}>
        + Hinzufügen
      </button>
    </fieldset>
  );
}

function RemoveButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" onClick={onClick}>
      Entfernen
    </button>
  );
}
