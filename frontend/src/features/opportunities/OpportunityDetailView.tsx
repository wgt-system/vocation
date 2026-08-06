import { useEffect, useState } from "react";

import { api, type OpportunityDetail } from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";

function displayValue(value: unknown) {
  return Array.isArray(value) ? value.join(", ") : String(value);
}

export function OpportunityDetailView({
  opportunityId,
  onBack,
}: {
  opportunityId: string;
  onBack: () => void;
}) {
  const [detail, setDetail] = useState<OpportunityDetail | null>(null);
  const [error, setError] = useState("");
  const [criterionId, setCriterionId] = useState("junior_suitability");
  const [value, setValue] = useState("3");
  const [reasoning, setReasoning] = useState("");
  const [decisionReason, setDecisionReason] = useState("");
  const [message, setMessage] = useState("");
  const reload = () =>
    api
      .getOpportunity(opportunityId)
      .then(setDetail)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Detail konnte nicht geladen werden.",
        ),
      );
  useEffect(() => {
    api
      .getOpportunity(opportunityId)
      .then(setDetail)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Detail konnte nicht geladen werden.",
        ),
      );
  }, [opportunityId]);
  if (error)
    return (
      <>
        <button onClick={onBack}>← Zurück</button>
        <ErrorState message={error} />
      </>
    );
  if (!detail) return <Loading />;
  async function saveAssessment() {
    try {
      await api.createPersonalAssessment(opportunityId, {
        criterion_id: criterionId,
        value: Number(value),
        reasoning: reasoning || null,
      });
      setMessage("Persönliches Assessment gespeichert.");
      setReasoning("");
      await reload();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Assessment konnte nicht gespeichert werden.",
      );
    }
  }
  async function setStatus(
    status:
      | "new"
      | "to_review"
      | "interesting"
      | "shortlisted"
      | "deferred"
      | "archived",
  ) {
    try {
      await api.changeStatus(
        opportunityId,
        status,
        decisionReason || undefined,
      );
      setMessage("Status gespeichert.");
      await reload();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Status konnte nicht gespeichert werden.",
      );
    }
  }
  async function exclude() {
    try {
      await api.exclude(opportunityId, decisionReason);
      setMessage("Opportunity ausgeschlossen.");
      setDecisionReason("");
      await reload();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Ausschluss konnte nicht gespeichert werden.",
      );
    }
  }
  async function restore() {
    try {
      await api.restore(
        opportunityId,
        "to_review",
        decisionReason || undefined,
      );
      setMessage("Opportunity wiederhergestellt.");
      await reload();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Restore konnte nicht gespeichert werden.",
      );
    }
  }
  return (
    <section>
      <button className="back" onClick={onBack}>
        ← Zurück zu Opportunities
      </button>
      <header className="detail-hero">
        <p className="eyebrow">{detail.company.name}</p>
        <h1>{detail.title}</h1>
        <p>
          {detail.locations
            .map((item) => `${item.label} (${item.precision})`)
            .join(" · ") || "Arbeitsort unbekannt"}
        </p>
        <strong>Status: {detail.tracking_status ?? "new"}</strong>
        {message && <p role="status">{message}</p>}
      </header>
      <div className="detail-grid">
        <section className="panel">
          <h2>Postings und Quellen</h2>
          {detail.postings.map((posting) => (
            <article className="record" key={posting.id}>
              <h3>{posting.title}</h3>
              <p>
                {posting.source.name} · beobachtet{" "}
                {new Date(posting.observed_at).toLocaleString("de-DE")}
              </p>
              <code className="url">{posting.source_reference.url}</code>
              {posting.published_at && (
                <small>Veröffentlicht: {posting.published_at}</small>
              )}
            </article>
          ))}
        </section>
        <section className="panel">
          <h2>External Assessments</h2>
          {(detail.external_assessments ?? detail.assessments).length === 0 ? (
            <p>Keine Assessments vorhanden.</p>
          ) : (
            (detail.external_assessments ?? detail.assessments).map((item) => (
              <article className="record" key={item.id}>
                <h3>{item.criterion_name}</h3>
                <strong>{displayValue(item.value)}</strong>
                {item.reasoning && <p>{item.reasoning}</p>}
                <small>{item.origin}</small>
              </article>
            ))
          )}
        </section>
        <section className="panel">
          <h2>Persönliche Assessments</h2>
          <div className="record">
            <label>
              Kriterium{" "}
              <input
                value={criterionId}
                onChange={(event) => setCriterionId(event.target.value)}
              />
            </label>
            <label>
              Wert{" "}
              <input
                type="number"
                min="1"
                max="5"
                value={value}
                onChange={(event) => setValue(event.target.value)}
              />
            </label>
            <label>
              Begründung{" "}
              <input
                value={reasoning}
                onChange={(event) => setReasoning(event.target.value)}
              />
            </label>
            <button onClick={saveAssessment}>Speichern</button>
          </div>
          {(detail.personal_assessments ?? []).map((item) => (
            <article className="record" key={item.id}>
              <h3>
                {item.criterion_name} · Revision {item.revision_number}
              </h3>
              <strong>{displayValue(item.value)}</strong>
              {item.reasoning && <p>{item.reasoning}</p>}
            </article>
          ))}
          <small>
            Historische Revisionen:{" "}
            {(detail.personal_assessment_history ?? []).length}
          </small>
        </section>
        <section className="panel">
          <h2>Persönliche Entscheidungen</h2>
          <label>
            Begründung{" "}
            <input
              value={decisionReason}
              onChange={(event) => setDecisionReason(event.target.value)}
            />
          </label>
          <div>
            <button onClick={() => setStatus("to_review")}>Zu prüfen</button>
            <button onClick={() => setStatus("interesting")}>
              Interessant
            </button>
            <button onClick={() => setStatus("shortlisted")}>Shortlist</button>
            {detail.tracking_status === "excluded" ? (
              <button onClick={restore}>Restore</button>
            ) : (
              <button onClick={exclude}>Ausschließen</button>
            )}
          </div>
          {(detail.decision_history ?? []).map((item) => (
            <article className="record" key={item.id}>
              <strong>
                {item.decision_type}: {item.previous_status} →{" "}
                {item.resulting_status}
              </strong>
              {item.reason && <p>{item.reason}</p>}
            </article>
          ))}
        </section>
        <section className="panel">
          <h2>Observations</h2>
          {detail.observations.length === 0 ? (
            <p>Keine Observations vorhanden.</p>
          ) : (
            detail.observations.map((item) => (
              <article className="record" key={item.id}>
                <h3>{item.type}</h3>
                <p>{displayValue(item.value)}</p>
                {item.evidence_summary && (
                  <small>{item.evidence_summary}</small>
                )}
              </article>
            ))
          )}
        </section>
        <section className="panel">
          <h2>Import-Provenienz</h2>
          <dl>
            <dt>Bundle</dt>
            <dd>{detail.import_provenance.bundle_id}</dd>
            <dt>Import</dt>
            <dd>
              <code>{detail.import_provenance.import_id}</code>
            </dd>
            <dt>Fingerprint</dt>
            <dd>
              <code className="fingerprint">
                {detail.import_provenance.fingerprint}
              </code>
            </dd>
          </dl>
        </section>
      </div>
    </section>
  );
}
