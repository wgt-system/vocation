import { type FormEvent, useEffect, useMemo, useState } from "react";

import {
  api,
  type Criterion,
  type GeneratedUpdatePrompt,
  type ImportReport,
  type UpdateMode,
  type UpdatePromptOptions,
} from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";
import { ImportReportView } from "../imports/ImportReportView";

type EvidenceKind = "observation" | "criterion";
type SubjectType = "company" | "opportunity" | "posting";
type GapDraft = {
  subjectType: SubjectType;
  subjectId: string;
  evidenceKind: EvidenceKind;
  observationType: UpdatePromptOptions["observation_types"][number] | "";
  criterionId: string;
};
type GeneratedState =
  | { kind: "initial"; promptText: string; bundleVersion: string }
  | { kind: "update"; result: GeneratedUpdatePrompt };

const labels: Record<UpdateMode | "initial", string> = {
  initial: "Initial Research",
  full_update: "Full Update",
  company_update: "Company Update",
  opportunity_update: "Opportunity Update",
  gap_filling: "Gap Filling",
};
const modes: (UpdateMode | "initial")[] = [
  "initial",
  "full_update",
  "company_update",
  "opportunity_update",
  "gap_filling",
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
  const [mode, setMode] = useState<UpdateMode | "initial">("initial");
  const [profile, setProfile] = useState("");
  const [constraints, setConstraints] = useState("");
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
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [importError, setImportError] = useState("");
  const [gapError, setGapError] = useState("");

  function clearGenerated() {
    setGenerated(null);
    setReport(null);
    setCopied(false);
  }
  function changeScope(change: () => void) {
    change();
    clearGenerated();
    setFormError("");
  }
  function changeMode(next: UpdateMode | "initial") {
    setMode(next);
    setSelectedIds([]);
    setGaps([]);
    setFormError("");
    setGapError("");
    clearGenerated();
  }

  useEffect(() => {
    if (mode === "initial") return;
    setOptionsLoading(true);
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
    if (type === "company")
      return options.companies.map((item) => ({
        id: item.id,
        label: item.name,
      }));
    if (type === "opportunity")
      return options.opportunities.map((item) => ({
        id: item.id,
        label: `${item.title} — ${companyNames.get(item.company_id) ?? "Unbekanntes Unternehmen"}`,
      }));
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
      if (patch.subjectType)
        Object.assign(updated, {
          subjectId: "",
          criterionId: "",
          observationType: "",
        });
      if (patch.evidenceKind)
        Object.assign(updated, { criterionId: "", observationType: "" });
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
        const result = await api.generatePrompt({
          search_profile: profile,
          constraints: constraints
            .split("\n")
            .map((item) => item.trim())
            .filter(Boolean),
          as_of_date: asOfDate,
        });
        setGenerated({
          kind: "initial",
          promptText: result.prompt_text,
          bundleVersion: result.bundle_version,
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
      generated?.kind === "initial"
        ? generated.promptText
        : generated?.result.prompt_text;
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
  }
  function savePrompt() {
    const text =
      generated?.kind === "initial"
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
      const next = await api.importText(content);
      setReport(next);
      if (next.status === "applied") onImported?.();
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
  }
  const promptText =
    generated?.kind === "initial"
      ? generated.promptText
      : generated?.result.prompt_text;

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">External Research</p>
          <h1>Research Prompt</h1>
        </div>
      </header>
      <form className="panel stack" onSubmit={generate}>
        <label>
          Research-Modus
          <select
            aria-label="Prompt-Modus"
            value={mode}
            onChange={(event) =>
              changeMode(event.target.value as UpdateMode | "initial")
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
          <>
            <label>
              Suchprofil
              <textarea
                rows={5}
                value={profile}
                onChange={(event) =>
                  changeScope(() => setProfile(event.target.value))
                }
                required
              />
            </label>
            <label>
              Constraints, eine pro Zeile
              <textarea
                rows={4}
                value={constraints}
                onChange={(event) =>
                  changeScope(() => setConstraints(event.target.value))
                }
              />
            </label>
          </>
        )}
        {mode === "company_update" && (
          <fieldset className="selection-list">
            <legend>Companies auswählen</legend>
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
            <legend>Opportunities auswählen</legend>
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
        {mode === "gap_filling" && (
          <div className="gap-requests">
            <h2>Gap-Anfragen</h2>
            {gaps.map((item, index) => (
              <div className="gap-request" key={index}>
                <label>
                  Subject Type
                  <select
                    value={item.subjectType}
                    onChange={(event) =>
                      updateGap(index, {
                        subjectType: event.target.value as SubjectType,
                      })
                    }
                  >
                    <option value="company">Company</option>
                    <option value="opportunity">Opportunity</option>
                    <option value="posting">Posting</option>
                  </select>
                </label>
                <label>
                  Subject
                  <select
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
                  Evidence Kind
                  <select
                    value={item.evidenceKind}
                    onChange={(event) =>
                      updateGap(index, {
                        evidenceKind: event.target.value as EvidenceKind,
                      })
                    }
                  >
                    <option value="observation">Observation</option>
                    <option value="criterion">Assessment Criterion</option>
                  </select>
                </label>
                {item.evidenceKind === "observation" ? (
                  <label>
                    Observation
                    <select
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
                    Assessment Criterion
                    <select
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
                  Request entfernen
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
              Request hinzufügen
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
            type="date"
            value={asOfDate}
            onChange={(event) =>
              changeScope(() => setAsOfDate(event.target.value))
            }
            required
          />
        </label>
        {optionsLoading && <Loading label="Update-Optionen werden geladen …" />}
        <button
          className="primary"
          type="submit"
          disabled={loading || optionsLoading}
        >
          {mode === "initial"
            ? "Self-contained Prompt erzeugen"
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
                  : generated.result.prompt_type
              ]
            }
          </p>
          <p>
            Bundle Version:{" "}
            <code>
              {generated.kind === "initial"
                ? generated.bundleVersion
                : generated.result.bundle_version}
            </code>
          </p>
          {generated.kind === "update" && (
            <>
              <p>
                Prompt Version: <code>{generated.result.prompt_version}</code>
              </p>
              <p>
                Prompt Context Ref:{" "}
                <code>{generated.result.prompt_context_ref}</code>
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
          <h2>Research-Ergebnis importieren</h2>
          <label>
            Datei auswählen
            <input
              aria-label="Research-Ergebnis JSON-Datei"
              type="file"
              accept="application/json,.json"
              onChange={(event) => selectFile(event.target.files?.[0])}
            />
          </label>
          <label>
            Oder JSON einfügen
            <textarea
              aria-label="Research-Ergebnis JSON"
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
        </section>
      )}
    </section>
  );
}
