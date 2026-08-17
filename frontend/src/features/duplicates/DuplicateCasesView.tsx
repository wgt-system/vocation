import { useEffect, useMemo, useState } from "react";

import {
  api,
  type DuplicateCaseReview,
  type DuplicateDecisionOutcome,
} from "../../api/client";

const outcomeLabels: Record<DuplicateDecisionOutcome, string> = {
  confirmed_duplicate: "Identisch",
  confirmed_distinct: "Getrennt",
  related_but_distinct: "Verwandt, aber getrennt",
  keep_unresolved: "Ungeklärt lassen",
};

const outcomes = Object.keys(outcomeLabels) as DuplicateDecisionOutcome[];
type ReviewFilter = "open" | "resolved" | "all";

const formatDate = (value: string) => new Date(value).toLocaleString("de-DE");

function defaultOutcome(item: DuplicateCaseReview): DuplicateDecisionOutcome {
  return (
    outcomes.find((outcome) => outcome !== item.current_decision?.outcome) ??
    "confirmed_duplicate"
  );
}

function reviewStatus(item: DuplicateCaseReview): string {
  if (!item.current_decision) return "Ungeprüft";
  if (item.current_decision.outcome === "keep_unresolved") {
    return "Geprüft · ungeklärt";
  }
  return `Entschieden · ${outcomeLabels[item.current_decision.outcome]}`;
}

export function DuplicateCasesView() {
  const [cases, setCases] = useState<DuplicateCaseReview[]>([]);
  const [filter, setFilter] = useState<ReviewFilter>("open");
  const [selectedOutcomes, setSelectedOutcomes] = useState<
    Record<string, DuplicateDecisionOutcome>
  >({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setLoadError("");
    api
      .listDuplicateCases()
      .then((items) => {
        if (active) setCases(items);
      })
      .catch((reason) => {
        if (active) {
          setLoadError(
            reason instanceof Error
              ? reason.message
              : "Dubletten konnten nicht geladen werden.",
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const visibleCases = useMemo(
    () =>
      cases.filter((item) => {
        if (filter === "open") return !item.is_resolved;
        if (filter === "resolved") return item.is_resolved;
        return true;
      }),
    [cases, filter],
  );

  async function saveDecision(item: DuplicateCaseReview) {
    const reason = (reasons[item.id] ?? "").trim();
    if (!reason) {
      setErrors((current) => ({
        ...current,
        [item.id]: "Bitte einen Entscheidungsgrund eingeben.",
      }));
      return;
    }
    const outcome = selectedOutcomes[item.id] ?? defaultOutcome(item);
    setErrors((current) => ({ ...current, [item.id]: "" }));
    setSaving((current) => ({ ...current, [item.id]: true }));
    try {
      const updated = await api.decideDuplicateCase(item.id, {
        outcome,
        reason,
      });
      setCases((current) =>
        current.map((entry) => (entry.id === item.id ? updated : entry)),
      );
      setReasons((current) => ({ ...current, [item.id]: "" }));
      setSelectedOutcomes((current) => {
        const next = { ...current };
        delete next[item.id];
        return next;
      });
    } catch (reason) {
      setErrors((current) => ({
        ...current,
        [item.id]:
          reason instanceof Error
            ? reason.message
            : "Entscheidung konnte nicht gespeichert werden.",
      }));
    } finally {
      setSaving((current) => ({ ...current, [item.id]: false }));
    }
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Review</p>
          <h2>Dubletten</h2>
          <p>
            Mögliche Opportunity- und Posting-Dubletten prüfen. Eine Entscheidung
            klassifiziert den Fall nur; sie führt keinen Merge aus.
          </p>
        </div>
        <label>
          Ansicht
          <select
            aria-label="Dubletten filtern"
            value={filter}
            onChange={(event) => setFilter(event.target.value as ReviewFilter)}
          >
            <option value="open">Offen</option>
            <option value="resolved">Entschieden</option>
            <option value="all">Alle</option>
          </select>
        </label>
      </div>

      {loading && <p>Lade Dubletten …</p>}
      {loadError && (
        <p className="state state-error" role="alert">
          {loadError}
        </p>
      )}
      {!loading && !loadError && visibleCases.length === 0 && (
        <p className="state">
          {cases.length === 0
            ? "Keine möglichen Dubletten vorhanden."
            : "Keine Dubletten in dieser Ansicht."}
        </p>
      )}

      {visibleCases.map((item) => {
        const selectedOutcome =
          selectedOutcomes[item.id] ?? defaultOutcome(item);
        return (
          <article className="record" key={item.id}>
            <div className="section-heading">
              <div>
                <strong>
                  {item.subject_type === "opportunity"
                    ? "Opportunity-Dublette"
                    : "Posting-Dublette"}
                </strong>
                <p>{reviewStatus(item)}</p>
              </div>
              <small>Erstellt: {formatDate(item.created_at)}</small>
            </div>

            <div className="comparison-grid">
              {[item.left_subject, item.right_subject].map((subject) => (
                <div className="record" key={subject.subject_id}>
                  <strong>{subject.title}</strong>
                  <p>{subject.context}</p>
                  <small>{subject.subject_id}</small>
                </div>
              ))}
            </div>

            <p>
              <strong>Evidenz:</strong> {item.evidence_summary}
            </p>
            {item.confidence !== null && (
              <p>
                <small>
                  Import-Konfidenz: {Math.round(item.confidence * 100)} %
                </small>
              </p>
            )}

            {item.source_references.length > 0 && (
              <div>
                <strong>Quellenbelege</strong>
                {item.source_references.map((source) => (
                  <p key={source.source_reference_id}>
                    <small>
                      {source.source_name}
                      {source.display_label ? ` · ${source.display_label}` : ""}
                      {` · ${formatDate(source.observed_at)}`}
                      <br />
                      <span>{source.url}</span>
                    </small>
                  </p>
                ))}
              </div>
            )}

            {item.current_decision && (
              <div>
                <strong>Aktuelle Entscheidung</strong>
                <p>
                  {outcomeLabels[item.current_decision.outcome]} · {" "}
                  {item.current_decision.reason}
                </p>
                <small>{formatDate(item.current_decision.decided_at)}</small>
              </div>
            )}

            {item.decision_history.length > 0 && (
              <details>
                <summary>
                  Entscheidungshistorie ({item.decision_history.length})
                </summary>
                {item.decision_history.map((decision) => (
                  <p key={decision.id}>
                    <small>
                      #{decision.sequence} · {outcomeLabels[decision.outcome]} · {" "}
                      {decision.reason} · {formatDate(decision.decided_at)}
                    </small>
                  </p>
                ))}
              </details>
            )}

            <div className="actions">
              <label>
                Entscheidung
                <select
                  aria-label={`Entscheidung für ${item.id}`}
                  value={selectedOutcome}
                  onChange={(event) =>
                    setSelectedOutcomes((current) => ({
                      ...current,
                      [item.id]: event.target.value as DuplicateDecisionOutcome,
                    }))
                  }
                >
                  {outcomes
                    .filter(
                      (outcome) =>
                        outcome !== item.current_decision?.outcome,
                    )
                    .map((outcome) => (
                      <option key={outcome} value={outcome}>
                        {outcomeLabels[outcome]}
                      </option>
                    ))}
                </select>
              </label>
              <label>
                Grund
                <input
                  aria-label={`Entscheidungsgrund für ${item.id}`}
                  value={reasons[item.id] ?? ""}
                  onChange={(event) =>
                    setReasons((current) => ({
                      ...current,
                      [item.id]: event.target.value,
                    }))
                  }
                />
              </label>
              <button
                type="button"
                disabled={saving[item.id]}
                onClick={() => void saveDecision(item)}
              >
                {saving[item.id]
                  ? "Speichere …"
                  : "Entscheidung speichern"}
              </button>
            </div>
            {errors[item.id] && (
              <p className="state state-error" role="alert">
                {errors[item.id]}
              </p>
            )}
          </article>
        );
      })}
    </section>
  );
}
