import { useEffect, useState } from "react";

import {
  api,
  type ApplicationCase,
  type ApplicationLifecycle,
  type ApplicationMaterial,
  type ApplicationMaterialKind,
} from "../../api/client";

const lifecycles: { value: ApplicationLifecycle; label: string }[] = [
  { value: "draft", label: "Entwurf" },
  { value: "ready", label: "Bereit" },
  { value: "submitted", label: "Eingereicht" },
  { value: "interviewing", label: "Vorstellungsgespräch" },
  { value: "offer", label: "Angebot" },
  { value: "accepted", label: "Angenommen" },
  { value: "rejected", label: "Abgelehnt" },
  { value: "withdrawn", label: "Zurückgezogen" },
];
const terminal = new Set<ApplicationLifecycle>([
  "accepted",
  "rejected",
  "withdrawn",
]);
const lifecycleLabel = (value: ApplicationLifecycle) =>
  lifecycles.find((item) => item.value === value)?.label ?? value;
const materialLabels: Record<ApplicationMaterialKind, string> = {
  cv: "Lebenslauf",
  cover_letter: "Anschreiben",
  other: "Sonstiges",
};
const formatDate = (value: string) => new Date(value).toLocaleString("de-DE");

export function ApplicationCasePanel({
  opportunityId,
}: {
  opportunityId: string;
}) {
  const [cases, setCases] = useState<ApplicationCase[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [materials, setMaterials] = useState<ApplicationMaterial[]>([]);
  const [lifecycle, setLifecycle] = useState<ApplicationLifecycle>("draft");
  const [kind, setKind] = useState<ApplicationMaterialKind>("cv");
  const [displayName, setDisplayName] = useState("");
  const [revisionNames, setRevisionNames] = useState<Record<string, string>>(
    {},
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const selected = cases.find((item) => item.id === selectedId) ?? null;
  async function loadMaterials(caseId: string) {
    setMaterials(await api.listApplicationMaterials(caseId));
  }

  async function loadCases(preferredId?: string) {
    setLoading(true);
    setError("");
    try {
      const next = await api.listApplicationCases(opportunityId);
      setCases(next);
      const preferred = next.find((item) => item.id === preferredId);
      const nextSelected =
        preferred ??
        next.find((item) => !terminal.has(item.lifecycle)) ??
        next[next.length - 1];
      setSelectedId(nextSelected?.id ?? "");
      if (nextSelected) {
        setLifecycle(
          lifecycles.find((item) => item.value !== nextSelected.lifecycle)
            ?.value ?? nextSelected.lifecycle,
        );
        await loadMaterials(nextSelected.id);
      } else setMaterials([]);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Bewerbungen konnten nicht geladen werden.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadCases();
  }, [opportunityId]);

  async function selectCase(caseId: string) {
    setSelectedId(caseId);
    const next = cases.find((item) => item.id === caseId);
    if (!next) return;
    setLifecycle(
      lifecycles.find((item) => item.value !== next.lifecycle)?.value ??
        next.lifecycle,
    );
    setError("");
    try {
      await loadMaterials(caseId);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unterlagen konnten nicht geladen werden.",
      );
    }
  }

  async function createCase() {
    setError("");
    try {
      const created = await api.createApplicationCase(opportunityId);
      setSuccess("Bewerbung angelegt.");
      await loadCases(created.id);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Bewerbung konnte nicht angelegt werden.",
      );
    }
  }

  async function saveLifecycle() {
    if (!selected) return;
    setError("");
    try {
      await api.changeApplicationCaseLifecycle(selected.id, lifecycle);
      setSuccess("Lebenszyklus gespeichert.");
      await loadCases(selected.id);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Lebenszyklus konnte nicht gespeichert werden.",
      );
    }
  }

  async function createMaterial() {
    if (!selected || !displayName.trim()) {
      setError("Bitte einen Namen für die Unterlage eingeben.");
      return;
    }
    setError("");
    try {
      await api.createApplicationMaterial(
        selected.id,
        kind,
        displayName.trim(),
      );
      setDisplayName("");
      setSuccess("Unterlage angelegt.");
      await loadMaterials(selected.id);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unterlage konnte nicht angelegt werden.",
      );
    }
  }

  async function reviseMaterial(material: ApplicationMaterial) {
    const name = (revisionNames[material.id] ?? material.display_name).trim();
    if (!name) {
      setError("Bitte einen Namen für die Revision eingeben.");
      return;
    }
    setError("");
    try {
      await api.reviseApplicationMaterial(material.id, name);
      setSuccess("Revision erstellt.");
      await loadMaterials(material.application_case_id);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Revision konnte nicht erstellt werden.",
      );
    }
  }

  return (
    <section className="panel">
      <h2>Bewerbung</h2>
      <p className="application-case-help">
        Bewerbungsunterlagen verwaltet Vocation derzeit als Metadaten.
      </p>
      {loading && <p>Lade Bewerbungen …</p>}
      {error && (
        <p className="state state-error" role="alert">
          {error}
        </p>
      )}
      {success && (
        <p className="state" role="status">
          {success}
        </p>
      )}
      {!loading && cases.length === 0 && (
        <div className="record">
          <p>Für diese Opportunity gibt es noch keine Bewerbung.</p>
          <button type="button" onClick={() => void createCase()}>
            Bewerbung anlegen
          </button>
        </div>
      )}
      {cases.length > 0 && (
        <>
          <label>
            Bewerbungen
            <select
              aria-label="Bewerbung auswählen"
              value={selectedId}
              onChange={(event) => void selectCase(event.target.value)}
            >
              {cases.map((item) => (
                <option key={item.id} value={item.id}>
                  {lifecycleLabel(item.lifecycle)} ·{" "}
                  {formatDate(item.created_at)} ·{" "}
                  {terminal.has(item.lifecycle) ? "historisch" : "aktiv"}
                </option>
              ))}
            </select>
          </label>
          {selected && (
            <div className="record">
              <p>
                Lebenszyklus:{" "}
                <strong>{lifecycleLabel(selected.lifecycle)}</strong>
              </p>
              <small>
                Erstellt: {formatDate(selected.created_at)} · aktualisiert:{" "}
                {formatDate(selected.updated_at)}
              </small>
              <h3>Lebenslauf</h3>
              {selected.lifecycle_events.map((event, index) => (
                <p key={`${event.occurred_at}-${index}`}>
                  <small>
                    {event.previous_status
                      ? `${lifecycleLabel(event.previous_status)} → `
                      : ""}
                    {lifecycleLabel(event.resulting_status)} ·{" "}
                    {formatDate(event.occurred_at)}
                  </small>
                </p>
              ))}
              {!terminal.has(selected.lifecycle) && (
                <div className="actions">
                  <label>
                    Neuer Lebenszyklus
                    <select
                      aria-label="Neuer Bewerbungsstatus"
                      value={lifecycle}
                      onChange={(event) =>
                        setLifecycle(event.target.value as ApplicationLifecycle)
                      }
                    >
                      {lifecycles
                        .filter((item) => item.value !== selected.lifecycle)
                        .map((item) => (
                          <option key={item.value} value={item.value}>
                            {item.label}
                          </option>
                        ))}
                    </select>
                  </label>
                  <button type="button" onClick={() => void saveLifecycle()}>
                    Lebenszyklus speichern
                  </button>
                </div>
              )}
              <h3>Bewerbungsunterlagen</h3>
              <p>
                Hier werden nur Unterlagen-Metadaten verwaltet; keine Datei wird
                hochgeladen.
              </p>
              <div className="record">
                <label>
                  Art
                  <select
                    aria-label="Unterlagenart"
                    value={kind}
                    onChange={(event) =>
                      setKind(event.target.value as ApplicationMaterialKind)
                    }
                  >
                    {Object.entries(materialLabels).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Name
                  <input
                    aria-label="Name der Unterlage"
                    value={displayName}
                    onChange={(event) => setDisplayName(event.target.value)}
                  />
                </label>
                <button type="button" onClick={() => void createMaterial()}>
                  Unterlage anlegen
                </button>
              </div>
              {materials.map((material) => (
                <article className="record" key={material.id}>
                  <strong>{materialLabels[material.kind]}</strong>
                  <p>
                    {material.display_name} · Revision {material.revision}
                  </p>
                  <small>Aktualisiert: {formatDate(material.updated_at)}</small>
                  <label>
                    Neuer Anzeigename
                    <input
                      aria-label={`Revision für ${material.display_name}`}
                      value={
                        revisionNames[material.id] ?? material.display_name
                      }
                      onChange={(event) =>
                        setRevisionNames((current) => ({
                          ...current,
                          [material.id]: event.target.value,
                        }))
                      }
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => void reviseMaterial(material)}
                  >
                    Revision erstellen
                  </button>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
