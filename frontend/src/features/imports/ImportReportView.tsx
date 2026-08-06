import type { ImportReport } from "../../api/client";

export function ImportReportView({ report }: { report: ImportReport }) {
  const statusLabel =
    report.status === "applied"
      ? "Import erfolgreich"
      : report.status === "duplicate"
        ? "Bundle bereits importiert"
        : "Import abgelehnt";
  return (
    <section className={`report report-${report.status}`} aria-live="polite">
      <h2>Import Report</h2>
      <p className="report-status">{statusLabel}</p>
      {report.bundle_id && (
        <p>
          Bundle: <code>{report.bundle_id}</code>
        </p>
      )}
      {report.duplicate_of_import_id && (
        <p>
          Bereits angewendeter Import:{" "}
          <code>{report.duplicate_of_import_id}</code>
        </p>
      )}
      {Object.keys(report.counts).length > 0 && (
        <dl className="counts">
          {Object.entries(report.counts).map(([name, count]) => (
            <div key={name}>
              <dt>{name}</dt>
              <dd>{count}</dd>
            </div>
          ))}
        </dl>
      )}
      {report.warnings.length > 0 && (
        <div>
          <h3>Warnungen</h3>
          <ul>
            {report.warnings.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {report.issues.length > 0 && (
        <div>
          <h3>Validierungsfehler</h3>
          <ul className="issues">
            {report.issues.map((issue, index) => (
              <li key={`${issue.path}-${index}`}>
                <strong>{issue.code}</strong> <code>{issue.path}</code>
                <span>{issue.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
