import { useEffect, useState } from "react";

import {
  api,
  type Criterion,
  type ExternalLink,
  type OpportunityDetail,
  type TrackingStatus,
} from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";

const transitionStatuses: {
  value: Exclude<TrackingStatus, "excluded">;
  label: string;
}[] = [
  { value: "new", label: "Neu" },
  { value: "to_review", label: "Zu prüfen" },
  { value: "interesting", label: "Interessant" },
  { value: "shortlisted", label: "Shortlist" },
  { value: "deferred", label: "Später" },
  { value: "archived", label: "Archiviert" },
];

function displayValue(value: unknown) {
  return Array.isArray(value) ? value.join(", ") : String(value);
}

function errorMessage(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback;
}

type Availability = "available" | "unavailable" | "uncertain" | "unknown";
const availabilityLabels: Record<Availability, string> = {
  available: "Verfügbar",
  unavailable: "Nicht verfügbar",
  uncertain: "Unsicher",
  unknown: "Unbekannt",
};

function availabilityOf(value: Availability | null | undefined): Availability {
  return value ?? "unknown";
}

function freshnessLabel(
  ageDays: number | null | undefined,
  checkedAt: string | null | undefined,
) {
  if (ageDays != null) return `${ageDays} Tage alt`;
  if (checkedAt)
    return `geprüft ${new Date(checkedAt).toLocaleString("de-DE")}`;
  return "Alter unbekannt";
}

export function OpportunityDetailView({
  opportunityId,
  onBack,
}: {
  opportunityId: string;
  onBack: () => void;
}) {
  const [detail, setDetail] = useState<OpportunityDetail | null>(null);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [loadError, setLoadError] = useState("");
  const [mutationError, setMutationError] = useState("");
  const [criterionId, setCriterionId] = useState("");
  const [value, setValue] = useState<unknown>("");
  const [reasoning, setReasoning] = useState("");
  const [statusReason, setStatusReason] = useState("");
  const [exclusionReason, setExclusionReason] = useState("");
  const [message, setMessage] = useState("");
  const [externalLinks, setExternalLinks] = useState<ExternalLink[]>([]);
  const [externalLinksLoading, setExternalLinksLoading] = useState(true);
  const [externalLinkError, setExternalLinkError] = useState("");
  const [openingExternalLink, setOpeningExternalLink] = useState("");

  async function reload() {
    const next = await api.getOpportunity(opportunityId);
    setDetail(next);
  }

  useEffect(() => {
    setLoadError("");
    Promise.all([api.getOpportunity(opportunityId), api.listCriteria()])
      .then(([nextDetail, nextCriteria]) => {
        setDetail(nextDetail);
        setCriteria(nextCriteria);
        const first = nextCriteria.find(
          (criterion) =>
            criterion.active &&
            criterion.applicable_subject_type === "opportunity",
        );
        setCriterionId(first?.criterion_id ?? "");
      })
      .catch((reason) =>
        setLoadError(
          errorMessage(reason, "Detail konnte nicht geladen werden."),
        ),
      );
  }, [opportunityId]);

  useEffect(() => {
    setExternalLinksLoading(true);
    setExternalLinkError("");
    api
      .listExternalLinks(opportunityId)
      .then(setExternalLinks)
      .catch((reason) =>
        setExternalLinkError(
          errorMessage(
            reason,
            "Originalanzeigen konnten nicht geladen werden.",
          ),
        ),
      )
      .finally(() => setExternalLinksLoading(false));
  }, [opportunityId]);

  useEffect(() => {
    const criterion = criteria.find(
      (item) => item.criterion_id === criterionId,
    );
    const currentAssessment = detail?.personal_assessments.find(
      (assessment) => assessment.criterion_id === criterionId,
    );
    if (criterion) {
      setValue(
        currentAssessment?.value ??
          (criterion.value_type === "boolean"
            ? false
            : criterion.value_type === "numeric"
              ? (criterion.numeric_min ?? "")
              : criterion.value_type === "categorical"
                ? (criterion.allowed_values?.[0] ?? "")
                : ""),
      );
    }
  }, [criterionId, criteria, detail]);

  if (loadError) {
    return (
      <>
        <button onClick={onBack}>← Zurück</button>
        <ErrorState message={loadError} />
      </>
    );
  }
  if (!detail) return <Loading />;

  const applicableCriteria = criteria.filter(
    (criterion) =>
      criterion.active && criterion.applicable_subject_type === "opportunity",
  );
  const selectedCriterion = criteria.find(
    (criterion) => criterion.criterion_id === criterionId,
  );
  const currentAssessment = detail.personal_assessments.find(
    (assessment) => assessment.criterion_id === criterionId,
  );
  const currentAssessmentIds = new Set(
    detail.personal_assessments.map((assessment) => assessment.id),
  );

  function assessmentValue(raw: string): unknown {
    if (!selectedCriterion) return raw;
    if (selectedCriterion.value_type === "numeric") return Number(raw);
    if (selectedCriterion.value_type === "boolean") return raw === "true";
    return raw;
  }

  async function saveAssessment() {
    if (!selectedCriterion) return;
    setMessage("");
    setMutationError("");
    try {
      const payload = {
        value,
        reasoning: reasoning || null,
      };
      if (currentAssessment) {
        await api.revisePersonalAssessment(
          opportunityId,
          currentAssessment.id,
          payload,
        );
        setMessage("Neue persönliche Assessment-Revision gespeichert.");
      } else {
        await api.createPersonalAssessment(opportunityId, {
          criterion_id: selectedCriterion.criterion_id,
          ...payload,
        });
        setMessage("Persönliches Assessment erstellt.");
      }
      setReasoning("");
      await reload();
    } catch (reason) {
      setMutationError(
        errorMessage(reason, "Assessment konnte nicht gespeichert werden."),
      );
    }
  }

  async function setStatus(status: Exclude<TrackingStatus, "excluded">) {
    setMessage("");
    setMutationError("");
    try {
      await api.changeStatus(opportunityId, status, statusReason || undefined);
      setMessage("Status gespeichert.");
      await reload();
    } catch (reason) {
      setMutationError(
        errorMessage(reason, "Status konnte nicht gespeichert werden."),
      );
    }
  }

  async function exclude() {
    setMessage("");
    setMutationError("");
    if (!exclusionReason.trim()) {
      setMutationError("Für den Ausschluss ist ein Grund erforderlich.");
      return;
    }
    try {
      await api.exclude(opportunityId, exclusionReason.trim());
      setExclusionReason("");
      setMessage("Opportunity ausgeschlossen.");
      await reload();
    } catch (reason) {
      setMutationError(
        errorMessage(reason, "Ausschluss konnte nicht gespeichert werden."),
      );
    }
  }

  async function restore() {
    setMessage("");
    setMutationError("");
    try {
      await api.restore(opportunityId);
      setMessage("Opportunity wiederhergestellt.");
      await reload();
    } catch (reason) {
      setMutationError(
        errorMessage(reason, "Restore konnte nicht gespeichert werden."),
      );
    }
  }

  async function openExternalLink(postingId?: string) {
    const key = postingId ?? "preferred";
    setOpeningExternalLink(key);
    setExternalLinkError("");
    try {
      await api.openExternalLink(opportunityId, postingId);
    } catch (reason) {
      setExternalLinkError(
        errorMessage(reason, "Originalanzeige konnte nicht geöffnet werden."),
      );
    } finally {
      setOpeningExternalLink("");
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
        {detail.groups && detail.groups.length > 0 && (
          <p className="group-membership-summary">
            Groups &amp; Waves:{" "}
            {detail.groups.map((group) => group.name).join(" · ")}
          </p>
        )}
        <p className="availability-summary">
          Availability:{" "}
          <strong>
            {availabilityLabels[availabilityOf(detail.availability)]}
          </strong>
          <small>
            {freshnessLabel(
              detail.availability_age_days,
              detail.availability_last_checked_at,
            )}
          </small>
        </p>
        <strong>Status: {detail.tracking_status}</strong>
        {message && <p role="status">{message}</p>}
        {mutationError && (
          <p className="state state-error" role="alert">
            {mutationError}
          </p>
        )}
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
              <p className="availability-summary">
                Availability:{" "}
                <strong>
                  {availabilityLabels[availabilityOf(posting.availability)]}
                </strong>
                <small>
                  {freshnessLabel(
                    posting.availability_age_days,
                    posting.availability_last_checked_at,
                  )}
                </small>
              </p>
              {posting.availability_history &&
                posting.availability_history.length > 0 && (
                  <div className="availability-history">
                    <strong>Availability-Historie</strong>
                    {posting.availability_history.map((entry) => (
                      <small key={entry.id}>
                        {entry.result} · beobachtet{" "}
                        {new Date(entry.observed_at).toLocaleString("de-DE")} ·
                        aufgezeichnet{" "}
                        {new Date(entry.recorded_at).toLocaleString("de-DE")} ·{" "}
                        {entry.evidence_summary}
                      </small>
                    ))}
                  </div>
                )}
              <code className="url">{posting.source_reference.url}</code>
              {posting.published_at && (
                <small>Veröffentlicht: {posting.published_at}</small>
              )}
            </article>
          ))}
          <div className="external-links-section">
            <div className="external-links-header">
              <div>
                <h3>Originalanzeigen</h3>
                <p className="external-links-help">
                  Öffnen erfolgt über die Vocation External Navigation API.
                </p>
              </div>
              {externalLinks.length > 0 && (
                <button
                  type="button"
                  onClick={() => void openExternalLink()}
                  disabled={openingExternalLink === "preferred"}
                >
                  {openingExternalLink === "preferred"
                    ? "Öffnen …"
                    : "Bevorzugte Originalanzeige öffnen"}
                </button>
              )}
            </div>
            {externalLinksLoading && (
              <Loading label="Originalanzeigen werden geladen …" />
            )}
            {externalLinkError && (
              <p className="state state-error" role="alert">
                {externalLinkError}
              </p>
            )}
            {!externalLinksLoading &&
              externalLinks.length === 0 &&
              !externalLinkError && (
                <p>Keine gültige Originalanzeige verfügbar</p>
              )}
            {externalLinks.length > 0 && (
              <div className="external-link-list">
                {externalLinks.map((link) => (
                  <div className="external-link-row" key={link.posting_id}>
                    <div>
                      <strong>{link.source_name}</strong>
                      {link.display_label && (
                        <span> · {link.display_label}</span>
                      )}
                      {link.preferred && (
                        <span className="preferred-marker"> · bevorzugt</span>
                      )}
                      <small>
                        Availability: {availabilityLabels[link.availability]} ·
                        beobachtet{" "}
                        {new Date(link.observed_at).toLocaleString("de-DE")}
                      </small>
                    </div>
                    <button
                      type="button"
                      onClick={() => void openExternalLink(link.posting_id)}
                      disabled={openingExternalLink === link.posting_id}
                    >
                      {openingExternalLink === link.posting_id
                        ? "Öffnen …"
                        : "Öffnen"}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
        <section className="panel">
          <h2>External Assessments</h2>
          {detail.external_assessments.length === 0 ? (
            <p>Keine Assessments vorhanden.</p>
          ) : (
            detail.external_assessments.map((item) => (
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
              Kriterium
              <select
                value={criterionId}
                onChange={(event) => setCriterionId(event.target.value)}
              >
                {applicableCriteria.map((criterion) => (
                  <option
                    key={criterion.criterion_id}
                    value={criterion.criterion_id}
                  >
                    {criterion.display_name}
                  </option>
                ))}
              </select>
            </label>
            {selectedCriterion?.value_type === "numeric" && (
              <label>
                Wert
                <input
                  type="number"
                  min={selectedCriterion.numeric_min ?? undefined}
                  max={selectedCriterion.numeric_max ?? undefined}
                  value={String(value)}
                  onChange={(event) =>
                    setValue(assessmentValue(event.target.value))
                  }
                />
              </label>
            )}
            {selectedCriterion?.value_type === "categorical" && (
              <label>
                Wert
                <select
                  value={String(value)}
                  onChange={(event) =>
                    setValue(assessmentValue(event.target.value))
                  }
                >
                  {selectedCriterion.allowed_values?.map((allowed) => (
                    <option key={allowed} value={allowed}>
                      {allowed}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {selectedCriterion?.value_type === "boolean" && (
              <label>
                Wert
                <select
                  value={String(value)}
                  onChange={(event) =>
                    setValue(assessmentValue(event.target.value))
                  }
                >
                  <option value="true">Ja</option>
                  <option value="false">Nein</option>
                </select>
              </label>
            )}
            {selectedCriterion?.value_type === "text" && (
              <label>
                Wert
                <textarea
                  value={String(value)}
                  onChange={(event) =>
                    setValue(assessmentValue(event.target.value))
                  }
                />
              </label>
            )}
            <label>
              Begründung
              <input
                value={reasoning}
                onChange={(event) => setReasoning(event.target.value)}
              />
            </label>
            <button
              className="primary"
              disabled={!selectedCriterion}
              onClick={saveAssessment}
            >
              {currentAssessment
                ? "Revision erstellen"
                : "Assessment erstellen"}
            </button>
          </div>
          <h3>Revisionen</h3>
          {detail.personal_assessment_history.length === 0 ? (
            <p>Keine persönlichen Assessment-Revisionen vorhanden.</p>
          ) : (
            detail.personal_assessment_history.map((item) => (
              <article className="record" key={item.id}>
                <h3>
                  {item.criterion_name} · Revision {item.revision_number}
                  {currentAssessmentIds.has(item.id)
                    ? " (aktuell)"
                    : " (historisch)"}
                </h3>
                <strong>{displayValue(item.value)}</strong>
                {item.reasoning && <p>{item.reasoning}</p>}
                <small>
                  Erstellt: {new Date(item.created_at).toLocaleString("de-DE")}
                </small>
              </article>
            ))
          )}
        </section>
        <section className="panel">
          <h2>Tracking und Entscheidungen</h2>
          <p>
            Aktueller Status: <strong>{detail.tracking_status}</strong>
          </p>
          {detail.tracking_status !== "excluded" && (
            <label>
              Statusgrund (optional)
              <input
                value={statusReason}
                onChange={(event) => setStatusReason(event.target.value)}
              />
            </label>
          )}
          <div className="actions">
            {detail.tracking_status === "excluded" ? (
              <button onClick={restore}>Restore</button>
            ) : (
              <>
                {transitionStatuses.map((status) => (
                  <button
                    key={status.value}
                    onClick={() => setStatus(status.value)}
                  >
                    {status.label}
                  </button>
                ))}
                <label>
                  Ausschlussgrund (erforderlich)
                  <input
                    value={exclusionReason}
                    onChange={(event) => setExclusionReason(event.target.value)}
                  />
                </label>
                <button onClick={exclude}>Ausschließen</button>
              </>
            )}
          </div>
          <h3>Decision History</h3>
          {detail.decision_history.length === 0 ? (
            <p>Keine Entscheidungen vorhanden.</p>
          ) : (
            [...detail.decision_history]
              .sort((a, b) => a.created_at.localeCompare(b.created_at))
              .map((item) => (
                <article className="record" key={item.id}>
                  <strong>
                    {item.decision_type}: {item.previous_status} →{" "}
                    {item.resulting_status}
                  </strong>
                  {item.reason && <p>{item.reason}</p>}
                  <small>
                    {new Date(item.created_at).toLocaleString("de-DE")}
                    {item.reverses_decision_id
                      ? " · macht eine frühere Entscheidung rückgängig"
                      : ""}
                  </small>
                </article>
              ))
          )}
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
