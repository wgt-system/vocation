import { useEffect, useState } from "react";

import { api, type OpportunityDetail } from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";

function displayValue(value: unknown) { return Array.isArray(value) ? value.join(", ") : String(value); }

export function OpportunityDetailView({ opportunityId, onBack }: { opportunityId: string; onBack: () => void }) {
  const [detail, setDetail] = useState<OpportunityDetail | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.getOpportunity(opportunityId).then(setDetail).catch((reason) => setError(reason instanceof Error ? reason.message : "Detail konnte nicht geladen werden.")); }, [opportunityId]);
  if (error) return <><button onClick={onBack}>← Zurück</button><ErrorState message={error} /></>;
  if (!detail) return <Loading />;
  return (
    <section>
      <button className="back" onClick={onBack}>← Zurück zu Opportunities</button>
      <header className="detail-hero"><p className="eyebrow">{detail.company.name}</p><h1>{detail.title}</h1><p>{detail.locations.map((item) => `${item.label} (${item.precision})`).join(" · ") || "Arbeitsort unbekannt"}</p></header>
      <div className="detail-grid">
        <section className="panel"><h2>Postings und Quellen</h2>{detail.postings.map((posting) => <article className="record" key={posting.id}><h3>{posting.title}</h3><p>{posting.source.name} · beobachtet {new Date(posting.observed_at).toLocaleString("de-DE")}</p><code className="url">{posting.source_reference.url}</code>{posting.published_at && <small>Veröffentlicht: {posting.published_at}</small>}</article>)}</section>
        <section className="panel"><h2>External Assessments</h2>{detail.assessments.length === 0 ? <p>Keine Assessments vorhanden.</p> : detail.assessments.map((item) => <article className="record" key={item.id}><h3>{item.criterion_name}</h3><strong>{displayValue(item.value)}</strong>{item.reasoning && <p>{item.reasoning}</p>}<small>{item.origin}</small></article>)}</section>
        <section className="panel"><h2>Observations</h2>{detail.observations.length === 0 ? <p>Keine Observations vorhanden.</p> : detail.observations.map((item) => <article className="record" key={item.id}><h3>{item.type}</h3><p>{displayValue(item.value)}</p>{item.evidence_summary && <small>{item.evidence_summary}</small>}</article>)}</section>
        <section className="panel"><h2>Import-Provenienz</h2><dl><dt>Bundle</dt><dd>{detail.import_provenance.bundle_id}</dd><dt>Import</dt><dd><code>{detail.import_provenance.import_id}</code></dd><dt>Fingerprint</dt><dd><code className="fingerprint">{detail.import_provenance.fingerprint}</code></dd></dl></section>
      </div>
    </section>
  );
}
