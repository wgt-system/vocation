import { useEffect, useState } from "react";

import {
  api,
  type OpportunityListItem,
  type TrackingStatus,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

type Availability = NonNullable<OpportunityListItem["availability"]>;
const availabilityLabels: Record<Availability, string> = {
  available: "Verfügbar",
  unavailable: "Nicht verfügbar",
  uncertain: "Unsicher",
  unknown: "Unbekannt",
};

function availabilityOf(item: OpportunityListItem): Availability {
  return item.availability ?? "unknown";
}

function freshnessLabel(item: OpportunityListItem) {
  if (item.availability_age_days != null) {
    return `${item.availability_age_days} Tage alt`;
  }
  if (item.availability_last_checked_at) {
    return `geprüft ${new Date(item.availability_last_checked_at).toLocaleDateString("de-DE")}`;
  }
  return "Alter unbekannt";
}

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
  const [statusFilter, setStatusFilter] = useState<TrackingStatus[]>([]);
  const [availabilityFilter, setAvailabilityFilter] = useState<
    Availability | "all"
  >("all");
  const statuses: { value: TrackingStatus; label: string }[] = [
    { value: "new", label: "Neu" },
    { value: "to_review", label: "Zu prüfen" },
    { value: "interesting", label: "Interessant" },
    { value: "shortlisted", label: "Shortlist" },
    { value: "deferred", label: "Später" },
    { value: "excluded", label: "Ausgeschlossen" },
    { value: "archived", label: "Archiviert" },
  ];
  const visibleItems = items.filter(
    (item) =>
      (statusFilter.length === 0 ||
        statusFilter.includes(item.tracking_status)) &&
      (availabilityFilter === "all" ||
        availabilityOf(item) === availabilityFilter),
  );
  function toggleStatus(status: TrackingStatus) {
    setStatusFilter((current) =>
      current.includes(status)
        ? current.filter((item) => item !== status)
        : [...current, status],
    );
  }
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
        <fieldset className="status-filters">
          <legend>Tracking Status filtern</legend>
          {statuses.map((status) => (
            <label key={status.value} className="checkbox-label">
              <input
                type="checkbox"
                checked={statusFilter.includes(status.value)}
                onChange={() => toggleStatus(status.value)}
              />
              {status.label}
            </label>
          ))}
          {statusFilter.length > 0 && (
            <button type="button" onClick={() => setStatusFilter([])}>
              Filter löschen
            </button>
          )}
        </fieldset>
        <span className="count-badge">{visibleItems.length}</span>
        <label>
          Availability
          <select
            aria-label="Availability filtern"
            value={availabilityFilter}
            onChange={(event) =>
              setAvailabilityFilter(event.target.value as Availability | "all")
            }
          >
            <option value="all">Alle</option>
            <option value="available">Verfügbar</option>
            <option value="unavailable">Nicht verfügbar</option>
            <option value="uncertain">Unsicher</option>
            <option value="unknown">Unbekannt</option>
          </select>
        </label>
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
        {visibleItems.map((item) => (
          <button
            className={`opportunity-card status-${item.tracking_status}`}
            key={item.id}
            onClick={() => onSelect(item.id)}
          >
            <span className="eyebrow">{item.company_name}</span>
            <strong>{item.title}</strong>
            <span>{item.locations.join(" · ") || "Arbeitsort unbekannt"}</span>
            <small>
              {item.posting_count} Posting · {item.assessment_count} Assessment
              · Status: {item.tracking_status}
            </small>
            <span
              className={`availability-badge availability-${availabilityOf(item)}`}
            >
              {availabilityLabels[availabilityOf(item)]}
            </span>
            <small>{freshnessLabel(item)}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
