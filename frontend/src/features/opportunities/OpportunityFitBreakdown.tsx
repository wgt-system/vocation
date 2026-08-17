import { useEffect, useState } from "react";

import { fitApi, type OpportunityFit } from "./fitApi";

const hardStatusLabels: Record<
  OpportunityFit["hard_constraint_status"],
  string
> = {
  pass: "Harte Kriterien erfüllt",
  fail: "Harte Kriterien nicht erfüllt",
  unknown: "Harte Kriterien teilweise offen",
};

function displayValue(value: unknown) {
  if (value === null || value === undefined) return "–";
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "boolean") return value ? "Ja" : "Nein";
  return String(value);
}

export function OpportunityFitBreakdown({ fit }: { fit: OpportunityFit }) {
  return (
    <section className="panel fit-breakdown">
      <div className="section-heading">
        <div>
          <h2>Fit &amp; Evidenz</h2>
          <p className="muted">
            Suchprofil Revision {fit.search_profile_revision} · Bewertung bleibt
            von Tracking und persönlichen Entscheidungen getrennt.
          </p>
        </div>
        <div className="fit-summary">
          <strong>
            {fit.weighted_fit_score === null
              ? "Fit offen"
              : `Fit ${fit.weighted_fit_score}%`}
          </strong>
          <span>Evidenz {fit.evidence_completeness}%</span>
          <span>{hardStatusLabels[fit.hard_constraint_status]}</span>
        </div>
      </div>

      {fit.hard_failures.length > 0 && (
        <div className="record">
          <strong>Harte Ausschlussgründe</strong>
          <ul>
            {fit.hard_failures.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {fit.hard_unknowns.length > 0 && (
        <div className="record">
          <strong>Offene harte Kriterien</strong>
          <ul>
            {fit.hard_unknowns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {fit.missing_evidence.length > 0 && (
        <div className="record">
          <strong>Fehlende oder nicht bewertbare Evidenz</strong>
          <ul>
            {fit.missing_evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="fit-contributions">
        {fit.contributions.map((contribution) => (
          <article className="record" key={contribution.criterion_id}>
            <h3>{contribution.criterion_name}</h3>
            <p>
              Wert: <strong>{displayValue(contribution.value)}</strong> ·
              Gewicht {contribution.weight}
            </p>
            {contribution.score !== null ? (
              <p>
                Normalisiert: {contribution.score}% · gewichtete Punkte:{" "}
                {contribution.weighted_points ?? 0}
              </p>
            ) : (
              <p>Status: {contribution.status}</p>
            )}
            {contribution.origin && (
              <small>Provenienz: {contribution.origin}</small>
            )}
            <p>{contribution.explanation}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export function OpportunityDetailFitPanel({
  opportunityId,
}: {
  opportunityId: string;
}) {
  const [fit, setFit] = useState<OpportunityFit | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    fitApi
      .get(opportunityId)
      .then((next) => {
        if (active) setFit(next);
      })
      .catch((reason) => {
        if (active) {
          setFit(null);
          setError(
            reason instanceof Error
              ? reason.message
              : "Fit konnte nicht geladen werden.",
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [opportunityId]);

  if (loading) {
    return (
      <section className="panel">
        <h2>Fit &amp; Evidenz</h2>
        <p className="muted">Fit wird geladen…</p>
      </section>
    );
  }

  if (error || !fit) {
    return (
      <section className="panel">
        <h2>Fit &amp; Evidenz</h2>
        <p className="muted">
          {error || "Für diese Opportunity ist noch kein Fit verfügbar."}
        </p>
      </section>
    );
  }

  return <OpportunityFitBreakdown fit={fit} />;
}
