import { useEffect, useState } from "react";

import { api, type OpportunityListItem } from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

export function OpportunityList({
  refreshToken,
  onSelect,
}: {
  refreshToken: number;
  onSelect: (id: string) => void;
}) {
  const [items, setItems] = useState<OpportunityListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  useEffect(() => {
    setLoading(true);
    api
      .listOpportunities()
      .then(setItems)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Opportunities konnten nicht geladen werden.",
        ),
      )
      .finally(() => setLoading(false));
  }, [refreshToken]);

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Persönlicher Stellenmarkt</p>
          <h1>Opportunities</h1>
        </div>
        <label>
          Filter{" "}
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="all">Alle</option>
            <option value="new">Neu</option>
            <option value="to_review">Zu prüfen</option>
            <option value="interesting">Interessant</option>
            <option value="shortlisted">Shortlist</option>
            <option value="deferred">Später</option>
            <option value="excluded">Ausgeschlossen</option>
            <option value="archived">Archiviert</option>
          </select>
        </label>
        <span className="count-badge">
          {
            items.filter(
              (item) =>
                statusFilter === "all" || item.tracking_status === statusFilter,
            ).length
          }
        </span>
      </header>
      {loading && <Loading />}
      {error && <ErrorState message={error} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState>
          <h2>Noch keine Opportunities</h2>
          <p>
            Erzeuge einen Research Prompt und importiere anschließend das JSON
            Bundle.
          </p>
        </EmptyState>
      )}
      <div className="opportunity-grid">
        {items
          .filter(
            (item) =>
              statusFilter === "all" || item.tracking_status === statusFilter,
          )
          .map((item) => (
            <button
              className="opportunity-card"
              key={item.id}
              onClick={() => onSelect(item.id)}
            >
              <span className="eyebrow">{item.company_name}</span>
              <strong>{item.title}</strong>
              <span>
                {item.locations.join(" · ") || "Arbeitsort unbekannt"}
              </span>
              <small>
                {item.posting_count} Posting · {item.assessment_count}{" "}
                Assessment · Status: {item.tracking_status}
              </small>
            </button>
          ))}
      </div>
    </section>
  );
}
