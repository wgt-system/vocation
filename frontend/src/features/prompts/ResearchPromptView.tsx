import { type FormEvent, useEffect, useMemo, useState } from "react";

import {
  api,
  type AvailabilityImportReport,
  type Criterion,
  type GeneratedUpdatePrompt,
  type ImportReport,
  type UpdateMode,
  type UpdatePromptOptions,
} from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";
import { ImportReportView } from "../imports/ImportReportView";
import {
  profileApi,
  type CandidateProfile,
  type SearchProfile,
} from "../profiles/profileApi";
import { initialResearchApi } from "./initialResearchApi";

type EvidenceKind = "observation" | "criterion";
type ResearchMode = UpdateMode | "availability_check";
type SubjectType = "company" | "opportunity" | "posting";
type GapDraft = {
  subjectType: SubjectType;
  subjectId: string;
  evidenceKind: EvidenceKind;
  observationType: UpdatePromptOptions["observation_types"][number] | "";
  criterionId: string;
};
type GeneratedState =
  | {
      kind: "initial";
      promptText: string;
      bundleVersion: string;
      promptRunId: string;
    }
  | { kind: "update"; result: GeneratedUpdatePrompt }
  | {
      kind: "availability";
      promptText: string;
      bundleVersion: string;
      promptVersion: string;
      promptContextRef: string;
    };

const labels: Record<ResearchMode | "initial", string> = {
  initial: "Neue Stellensuche",
  full_update: "Gesamten Stellenmarkt aktualisieren",
  company_update: "Unternehmen aktualisieren",
  opportunity_update: "Stelle aktualisieren",
  gap_filling: "Fehlende Informationen recherchieren",
  availability_check: "Verfügbarkeit prüfen",
};
const modes: (ResearchMode | "initial")[] = [
  "initial",
  "full_update",
  "company_update",
  "opportunity_update",
  "gap_filling",
  "availability_check",
];

function emptyGap(): GapDraft {
  return {
    subjectType: "company",
    subjectId: "",
    evidenceKind: "observation",
    observationType: "",
    criterionId: "",
  };
}

export function ResearchPromptView({
  onImported,
}: {
  onImported?: () => void;
}) {
  const [mode, setMode] = useState<ResearchMode | "initial">("initial");
  const [searchProfiles, setSearchProfiles] = useState<SearchProfile[]>([]);
  const [selectedSearchProfileId, setSelectedSearchProfileId] = useState("");
  const [candidateProfile, setCandidateProfile] =
    useState<CandidateProfile | null>(null);
  const [includeCandidateProfile, setIncludeCandidateProfile] = useState(true);
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [options, setOptions] = useState<UpdatePromptOptions | null>(null);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [gaps, setGaps] = useState<GapDraft[]>([]);
  const [generated, setGenerated] = useState<GeneratedState | null>(null);
  const [content, setContent] = useState("");
  const [report, setReport] = useState<ImportReport | null>(null);
  const [availabilityReport, setAvailabilityReport] =
    useState<AvailabilityImportReport | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [initialOptionsLoading, setInitialOptionsLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [importError, setImportError] = useState("");
  const [gapError, setGapError] = useState("");

  const selectedSearchProfile = useMemo(
    () =>
      searchProfiles.find(
        (profile) => profile.id === selectedSearchProfileId,
      ) ?? null,
    [searchProfiles, selectedSearchProfileId],
  );

  function clearGenerated() {
    setGenerated(null);
    setReport(null);
    setAvailabilityReport(null);
    setCopied(false);
  }

  function changeScope(change: () => void) {
    change();
    clearGenerated();
    setFormError("");
  }

  function changeMode(next: ResearchMode | "initial") {
    setMode(next);
    setSelectedIds([]);
    setGaps([]);
    setFormError("");
    setGapError("");
    setError("");
    clearGenerated();
  }

  useEffect(() => {
    if (mode !== "initial") return;
    setInitialOptionsLoading(true);
    setError("");
    Promise.all([profileApi.listSearchProfiles(), profileApi.getCandidate()])
      .then(([profiles, candidate]) => {
        setSearchProfiles(profiles);
        setCandidateProfile(candidate);
        setIncludeCandidateProfile(candidate !== null);
        setSelectedSearchProfileId((current) => {
          if (profiles.some((profile) => profile.id === current))
            return current;
          return (
            profiles.find((profile) => profile.is_default)?.id ??
            profiles[0]?.id ??
            ""
          );
        });
      })
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Profile konnten nicht geladen werden.",
        ),
      )
      .finally(() => setInitialOptionsLoading(false));
  }, [mode]);

  useEffect(() => {
    if (mode === "initial") return;
    setOptionsLoading(true);
    setError("");
    const request =
      mode === "gap_filling"
        ? Promise.all([api.getUpdatePromptOptions(), api.listCriteria()]).then(
            ([nextOptions, nextCriteria]) => {
              setOptions(nextOptions);
              setCriteria(nextCriteria);
            },
          )
        : api.getUpdatePromptOptions().then(setOptions);
    request
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Update-Optionen konnten nicht geladen werden.",
        ),
      )
      .finally(() => setOptionsLoading(false));
  }, [mode]);

  const companyNames = useMemo(
    () =>
      new Map((options?.companies ?? []).map((item) => [item.id, item.name])),
    [options],
  );

  function toggleId(id: string) {
    changeScope(() =>
      setSelectedIds((current) =>
        current.includes(id)
          ? current.filter((item) => item !== id)
          : [...current, id],
      ),
    );
  }

  function subjects(type: SubjectType) {
    if (!options) return [];
    if (type === "company") {
      return options.companies.map((item) => ({
        id: item.id,
        label: item.name,
      }));
    }
    if (type === "opportunity") {
      return options.opportunities.map((item) => ({
        id: item.id,
        label: `${item.title} — ${companyNames.get(item.company_id) ?? "Unbekanntes Unternehmen"}`,
      }));
    }
    return options.postings.map((item) => ({ id: item.id, label: item.title }));
  }

  function applicableCriteria(type: SubjectType) {
    return criteria.filter(
      (item) => item.active && item.applicable_subject_type === type,
    );
  }

  function gapKey(item: GapDraft) {
    return [
      item.subjectType,
      item.subjectId,
      item.evidenceKind,
      item.observationType,
      item.criterionId,
    ].join("|");
  }

  function updateGap(index: number, patch: Partial<GapDraft>) {
    const next = gaps.map((item, itemIndex) => {
      if (itemIndex !== index) return item;
      const updated = { ...item, ...patch };
      if (patch.subjectType) {
        Object.assign(updated, {
          subjectId: "",
          criterionId: "",
          observationType: "",
        });
      }
      if (patch.evidenceKind) {
        Object.assign(updated, { criterionId: "", observationType: "" });
      }
      return updated;
    });
    const keys = next.map(gapKey);
    if (keys.some((key, itemIndex) => keys.indexOf(key) !== itemIndex)) {
      setGapError("Doppelte Gap-Anfragen sind nicht zulässig.");
      return;
    }
    changeScope(() => setGaps(next));
    setGapError("");
  }

  function removeGap(index: number) {
    changeScope(() =>
      setGaps((current) =>
        current.filter((_, itemIndex) => itemIndex !== index),
      ),
    );
  }

  function validGaps() {
    return (
      gaps.length > 0 &&
      gaps.every(
        (item) =>
          Boolean(item.subjectId) &&
          Boolean(
            item.evidenceKind === "observation"
              ? item.observationType
              : item.criterionId,
          ),
      )
    );
  }

  async function generate(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setFormError("");
    setGapError("");
    clearGenerated();
    try {
      if (mode === "initial") {
        if (!selectedSearchProfileId) {
          setFormError(
            "Lege zuerst unter „Profil & Suche“ ein Search Profile an.",
          );
          return;
        }
        const result = await initialResearchApi.generate(
          {
            search_profile: selectedSearchProfileId,
            constraints: [],
            as_of_date: asOfDate,
          },
          includeCandidateProfile && candidateProfile !== null,
        );
        setGenerated({
          kind: "initial",
          promptText: result.prompt_text,
          bundleVersion: result.bundle_version,
          promptRunId: result.prompt_run_id,
        });
        return;
      }
      if (mode === "availability_check") {
        if (selectedIds.length === 0) {
          setFormError("Mindestens ein Posting muss ausgewählt werden.");
          return;
        }
        const result = await api.generateAvailabilityPrompt({
          posting_ids: selectedIds,
          as_of_date: asOfDate,
        });
        setGenerated({
          kind: "availability",
          promptText: result.prompt_text,
          bundleVersion: result.bundle_version,
          promptVersion: result.prompt_version,
          promptContextRef: result.prompt_context_ref,
        });
        return;
      }
      if (
        mode !== "full_update" &&
        mode !== "gap_filling" &&
        selectedIds.length === 0
      ) {
        setFormError("Mindestens ein Eintrag muss ausgewählt werden.");
        return;
      }
      if (mode === "gap_filling" && !validGaps()) {
        setGapError(
          "Mindestens eine vollständige Gap-Anfrage ist erforderlich.",
        );
        return;
      }
      const result = await api.generateUpdatePrompt({
        mode,
        as_of_date: asOfDate,
        ...(mode === "company_update" || mode === "opportunity_update"
          ? { selected_ids: selectedIds }
          : {}),
        ...(mode === "gap_filling"
          ? {
              gap_requests: gaps.map((item) => ({
                subject_id: item.subjectId,
                subject_type: item.subjectType,
                observation_type:
                  item.evidenceKind === "observation"
                    ? item.observationType || null
                    : null,
                criterion_id:
                  item.evidenceKind === "criterion"
                    ? item.criterionId || null
                    : null,
              })),
            }
          : {}),
      });
      setGenerated({ kind: "update", result });
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Prompt konnte nicht erzeugt werden.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function copyPrompt() {
    const text =
      generated?.kind === "initial" || generated?.kind === "availability"
        ? generated.promptText
        : generated?.result.prompt_text;
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
  }

  function savePrompt() {
    const text =
      generated?.kind === "initial" || generated?.kind === "availability"
        ? generated.promptText
        : generated?.result.prompt_text;
    if (!text) return;
    const url = URL.createObjectURL(
      new Blob([text], { type: "text/plain;charset=utf-8" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `vocation-${mode === "initial" ? "initial-research" : mode}-${asOfDate}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function importResult() {
    setImportLoading(true);
    setImportError("");
    try {
      if (generated?.kind === "availability") {
        const next = await api.importAvailabilityText(content);
        setAvailabilityReport(next);
        if (next.status === "applied") onImported?.();
      } else if (generated?.kind === "initial") {
        const next = await initialResearchApi.importText(
          content,
          generated.promptRunId,
        );
        setReport(next);
        if (next.status === "applied") onImported?.();
      } else {
        const next = await api.importText(content);
        setReport(next);
        if (next.status === "applied") onImported?.();
      }
    } catch (reason) {
      setImportError(
        reason instanceof Error ? reason.message : "Import fehlgeschlagen.",
      );
    } finally {
      setImportLoading(false);
    }
  }

  async function selectFile(file?: File) {
    if (!file) return;
    setContent(await file.text());
    setReport(null);
    setAvailabilityReport(null);
  }

  const promptText =
    generated?.kind === "initial" || generated?.kind === "availability"
      ? generated.promptText
      : generated?.result.prompt_text;

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Externe Recherche</p>
          <h1>Recherche</h1>
        </div>
      </header>
      <form className="panel stack" onSubmit={generate}>
        <label>
          Rechercheart
          <select
            aria-label="Prompt-Modus"
            value={mode}
            onChange={(event) =>
              changeMode(event.target.value as ResearchMode | "initial")
            }
          >
            {modes.map((item) => (
              <option key={item} value={item}>
                {labels[item]}
              </option>
            ))}
          </select>
        </label>

        {mode === "initial" && (
          <div className="stack initial-research-options">
            <label>
              Search Profile
              <select
                aria-label="Search Profile"
                value={selectedSearchProfileId}
                onChange={(event) =>
                  changeScope(() =>
                    setSelectedSearchProfileId(event.target.value),
                  )
                }
              >
                {searchProfiles.length === 0 && (
                  <option value="">Kein Search Profile vorhanden</option>
                )}
                {searchProfiles.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} · Revision {profile.revision}
                    {profile.is_default ? " · Standard" : ""}
                  </option>
                ))}
              </select>
            </label>

            {selectedSearchProfile && (
              <div className="record">
                <strong>{selectedSearchProfile.name}</strong>
                <p>{selectedSearchProfile.description}</p>
                <small>
                  Revision {selectedSearchProfile.revision} · bis zu{" "}
                  {selectedSearchProfile.result_limit} Ergebnisse · Rollen:{" "}
                  {selectedSearchProfile.target_roles.join(", ")}
                </small>
              </div>
            )}

            <div className="record">
              <label className="checkbox-label">
                <input
                  aria-label="Candidate Profile einbeziehen"
                  type="checkbox"
                  checked={includeCandidateProfile && candidateProfile !== null}
                  disabled={candidateProfile === null}
                  onChange={(event) =>
                    changeScope(() =>
                      setIncludeCandidateProfile(event.target.checked),
                    )
                  }
                />
                Candidate Profile in externen Prompt einbeziehen
              </label>
              {candidateProfile ? (
                <p className="muted">
                  Revision {candidateProfile.revision} ·{" "}
                  {candidateProfile.headline}
                </p>
              ) : (
                <p className="muted">
                  Kein Candidate Profile vorhanden. Die Recherche nutzt nur das
                  Search Profile.
                </p>
              )}
              <p className="muted">
                Beim Kopieren verlässt der sichtbare Prompt Vocation. Aktivierte
                Candidate-Daten sind darin als Recherchekontext enthalten; sie
                werden nicht Bestandteil des Research Bundles.
              </p>
            </div>
          </div>
        )}

        {mode === "company_update" && (
          <fieldset className="selection-list">
            <legend>Unternehmen auswählen</legend>
            {options?.companies.map((item) => (
              <label key={item.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleId(item.id)}
                />
                {item.name}
              </label>
            ))}
          </fieldset>
        )}

        {mode === "opportunity_update" && (
          <fieldset className="selection-list">
            <legend>Stellen auswählen</legend>
            {options?.opportunities.map((item) => (
              <label key={item.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleId(item.id)}
                />
                {item.title} —{" "}
                {companyNames.get(item.company_id) ?? "Unbekanntes Unternehmen"}
              </label>
            ))}
          </fieldset>
        )}

        {mode === "availability_check" && (
          <fieldset className="selection-list">
            <legend>Stellenanzeigen auswählen</legend>
            {options?.postings.map((item) => (
              <label key={item.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleId(item.id)}
                />
                {item.title}
              </label>
            ))}
          </fieldset>
        )}

        {mode === "gap_filling" && (
          <div className="gap-requests">
            <h2>Fehlende Informationen</h2>
            {gaps.map((item, index) => (
              <div className="gap-request" key={gapKey(item) || index}>
                <label>
                  Bezugstyp
                  <select
                    aria-label="Subject Type"
                    value={item.subjectType}
                    onChange={(event) =>
                      updateGap(index, {
                        subjectType: event.target.value as SubjectType,
                      })
                    }
                  >
                    <option value="company">Unternehmen</option>
                    <option value="opportunity">Stelle</option>
                    <option value="posting">Stellenanzeige</option>
                  </select>
                </label>
                <label>
                  Bezug
                  <select
                    aria-label="Subject"
                    value={item.subjectId}
                    onChange={(event) =>
                      updateGap(index, { subjectId: event.target.value })
                    }
                  >
                    <option value="">Auswählen …</option>
                    {subjects(item.subjectType).map((subject) => (
                      <option key={subject.id} value={subject.id}>
                        {subject.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Evidenzart
                  <select
                    aria-label="Evidence Kind"
                    value={item.evidenceKind}
                    onChange={(event) =>
                      updateGap(index, {
                        evidenceKind: event.target.value as EvidenceKind,
                      })
                    }
                  >
                    <option value="observation">Beobachtung</option>
                    <option value="criterion">Bewertungskriterium</option>
                  </select>
                </label>
                {item.evidenceKind === "observation" ? (
                  <label>
                    Beobachtung
                    <select
                      aria-label="Observation"
                      value={item.observationType}
                      onChange={(event) =>
                        updateGap(index, {
                          observationType: event.target
                            .value as GapDraft["observationType"],
                        })
                      }
                    >
                      <option value="">Auswählen …</option>
                      {options?.observation_types.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : (
                  <label>
                    Bewertungskriterium
                    <select
                      aria-label="Assessment Criterion"
                      value={item.criterionId}
                      onChange={(event) =>
                        updateGap(index, { criterionId: event.target.value })
                      }
                    >
                      <option value="">Auswählen …</option>
                      {applicableCriteria(item.subjectType).map((criterion) => (
                        <option
                          key={criterion.criterion_id}
                          value={criterion.criterion_id}
                        >
                          {criterion.display_name}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
                <button type="button" onClick={() => removeGap(index)}>
                  Anfrage entfernen
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() =>
                changeScope(() =>
                  setGaps((current) => [...current, emptyGap()]),
                )
              }
            >
              Anfrage hinzufügen
            </button>
            {gapError && (
              <p className="state state-error" role="alert">
                {gapError}
              </p>
            )}
          </div>
        )}

        <label>
          Stichtag
          <input
            aria-label="Stichtag"
            type="date"
            value={asOfDate}
            onChange={(event) =>
              changeScope(() => setAsOfDate(event.target.value))
            }
            required
          />
        </label>
        {initialOptionsLoading && mode === "initial" && (
          <Loading label="Profile werden geladen …" />
        )}
        {optionsLoading && <Loading label="Update-Optionen werden geladen …" />}
        <button
          className="primary"
          type="submit"
          disabled={loading || optionsLoading || initialOptionsLoading}
        >
          {mode === "initial"
            ? "Profilbasierten Prompt erzeugen"
            : "Prompt erzeugen"}
        </button>
        {loading && <Loading label="Prompt wird erzeugt …" />}
        {formError && (
          <p className="state state-error" role="alert">
            {formError}
          </p>
        )}
        {error && <ErrorState message={error} />}
      </form>

      {generated && promptText && (
        <div className="panel stack">
          <h2>Generierter Prompt</h2>
          <p>
            Modus:{" "}
            {
              labels[
                generated.kind === "initial"
                  ? "initial"
                  : generated.kind === "availability"
                    ? "availability_check"
                    : generated.result.prompt_type
              ]
            }
          </p>
          <p>
            Bundle Version:{" "}
            <code>
              {generated.kind === "initial"
                ? generated.bundleVersion
                : generated.kind === "availability"
                  ? generated.bundleVersion
                  : generated.result.bundle_version}
            </code>
          </p>
          {generated.kind === "initial" && (
            <p>
              Prompt Run: <code>{generated.promptRunId}</code>
            </p>
          )}
          {(generated.kind === "update" ||
            generated.kind === "availability") && (
            <>
              <p>
                Prompt Version:{" "}
                <code>
                  {generated.kind === "availability"
                    ? generated.promptVersion
                    : generated.result.prompt_version}
                </code>
              </p>
              <p>
                Prompt Context Ref:{" "}
                <code>
                  {generated.kind === "availability"
                    ? generated.promptContextRef
                    : generated.result.prompt_context_ref}
                </code>
              </p>
            </>
          )}
          <textarea
            aria-label="Generierter Prompt"
            className="prompt-output"
            rows={22}
            readOnly
            value={promptText}
          />
          <div className="actions">
            <button className="primary" type="button" onClick={copyPrompt}>
              In Zwischenablage kopieren
            </button>
            <button type="button" onClick={savePrompt}>
              Als Textdatei speichern
            </button>
            {copied && <span role="status">Kopiert.</span>}
          </div>
        </div>
      )}

      {generated && (
        <section className="panel stack">
          <h2>Recherche-Ergebnis importieren</h2>
          <label>
            Datei auswählen
            <input
              aria-label={
                generated.kind === "availability"
                  ? "Verfügbarkeits-Ergebnis JSON-Datei"
                  : "Recherche-Ergebnis JSON-Datei"
              }
              type="file"
              accept="application/json,.json"
              onChange={(event) => selectFile(event.target.files?.[0])}
            />
          </label>
          <label>
            Oder JSON einfügen
            <textarea
              aria-label={
                generated.kind === "availability"
                  ? "Verfügbarkeits-Ergebnis JSON"
                  : "Recherche-Ergebnis JSON"
              }
              rows={14}
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="{ ... }"
            />
          </label>
          <button
            className="primary"
            type="button"
            onClick={importResult}
            disabled={!content.trim() || importLoading}
          >
            Bundle validieren und importieren
          </button>
          {importLoading && (
            <Loading label="Bundle wird validiert und importiert …" />
          )}
          {importError && <ErrorState message={importError} />}
          {report && <ImportReportView report={report} />}
          {availabilityReport && (
            <ImportReportView report={availabilityReport} />
          )}
        </section>
      )}
    </section>
  );
}
