import { useState } from "react";

import { api, type ImportReport } from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";
import { ImportReportView } from "./ImportReportView";

export function ImportView({ onImported }: { onImported: () => void }) {
  const [content, setContent] = useState("");
  const [report, setReport] = useState<ImportReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function selectFile(file?: File) {
    if (!file) return;
    setContent(await file.text());
    setReport(null);
  }

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const next = await api.importText(content);
      setReport(next);
      if (next.status === "applied") onImported();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Import fehlgeschlagen.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <header className="page-header"><div><p className="eyebrow">Research Intake</p><h1>Research Bundle importieren</h1></div></header>
      <div className="panel stack">
        <label>Datei auswählen<input aria-label="JSON-Datei" type="file" accept="application/json,.json" onChange={(event) => selectFile(event.target.files?.[0])} /></label>
        <label>Oder JSON einfügen<textarea aria-label="Research Bundle JSON" rows={14} value={content} onChange={(event) => setContent(event.target.value)} placeholder="{ ... }" /></label>
        <button className="primary" onClick={submit} disabled={!content.trim() || loading}>Bundle validieren und importieren</button>
        {loading && <Loading label="Bundle wird validiert und atomar importiert …" />}
        {error && <ErrorState message={error} />}
      </div>
      {report && <ImportReportView report={report} />}
    </section>
  );
}
