import { useEffect, useState } from "react";

import {
  api,
  type OpportunityGroup,
  type OpportunityComparison,
  type OpportunityListItem,
  type TrackingStatus,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";
import { MapView } from "./MapView";
import { OpportunityComparisonView } from "./OpportunityComparisonView";
import { OpportunityFitBreakdown } from "./OpportunityFitBreakdown";
import { fitApi, type OpportunityFit } from "./fitApi";

type Availability = NonNullable<OpportunityListItem["availability"]>;
type DisplayMode = "list" | "map";
type FitSort = "default" | "fit_desc";

const availabilityLabels: Record<Availability, string> = {
  available: "Verfügbar",
  unavailable: "Nicht verfügbar",
  uncertain: "Unsicher",
  unknown: "Unbekannt",
};

const hardStatusLabels: Record<
  OpportunityFit["hard_constraint_status"],
  string
> = {
  pass: "Harte Kriterien erfüllt",
  fail: "Harte Kriterien nicht erfüllt",
  unknown: "Harte Kriterien offen",
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
  const [groups, setGroups] = useState<OpportunityGroup[]>([]);
  const [groupFilter, setGroupFilter] = useState("");
  const [displayMode, setDisplayMode] = useState<DisplayMode>("list");
  const [selectedItems, setSelectedItems] = useState<OpportunityListItem[]>([]);
  const [comparison, setComparison] = useState<OpportunityComparison | null>(
    null,
  );
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonError, setComparisonError] = useState("");
  const [fits, setFits] = useState<Record<string, OpportunityFit>>({});
  const [fitLoading, setFitLoading] = useState(false);
  const [fitError, setFitError] = useState("");
  const [fitSort, setFitSort] = useState<FitSort>("default");
  const [expandedFitId, setExpandedFitId] = useState("");
  const statuses: { value: TrackingStatus; label: string }[] = [
    { value: "new", label: "Neu" },
    { value: "to_review", label: "Zu prüfen" },
    { value: "interesting", label: "Interessant" },
    { value: "shortlisted", label: "Shortlist" },
    { value: "deferred", label: "Später" },
    { value: "excluded", label: "Ausgeschlossen" },
    { value: "archived", label: "Archiviert" },
  ];
  const filteredItems = items.filter(
    (item) =>
      (statusFilter.length === 0 ||
        statusFilter.includes(item.tracking_status)) &&
      (availabilityFilter === "all" ||
        availabilityOf(item) === availabilityFilter),
  );
  const visibleItems =
    fitSort === "fit_desc"
      ? [...filteredItems].sort((left, right) => {
          const leftScore = fits[left.id]?.weighted_fit_score;
          const rightScore = fits[right.id]?.weighted_fit_score;
          if (leftScore === null || leftScore === undefined) {
            return rightScore === null || rightScore === undefined ? 0 : 1;
          }
          if (rightScore === null || rightScore === undefined) return -1;
          return rightScore - leftScore;
        })
      : filteredItems;

  function toggleStatus(status: TrackingStatus) {
    setStatusFilter((current) =>
      current.includes(status)
        ? current.filter((item) => item !== status)
        : [...current, status],
    );
  }

  useEffect(() => {
    setLoading(true);
    setError("");
    api
      .listOpportunities(groupFilter || undefined)
      .then(setItems)
      .catch((reason) =>
        setError(
          reason instanceof Error
            ? reason.message
            : "Opportunities konnten nicht geladen werden.",
        ),
      )
      .finally(() => setLoading(false));
  }, [groupFilter, refreshToken]);

  useEffect(() => {
    api
      .listGroups()
      .then(setGroups)
      .catch(() => setGroups([]));
  }, []);

  useEffect(() => {
    let active = true;
    if (items.length === 0) {
      setFits({});
      setFitError("");
      setFitLoading(false);
      return () => {
        active = false;
      };
    }
    setFitLoading(true);
    setFitError("");
    fitApi
      .list(items.map((item) => item.id))
      .then((nextFits) => {
        if (!active) return;
        setFits(
          Object.fromEntries(nextFits.map((fit) => [fit.opportunity_id, fit])),
        );
      })
      .catch((reason) => {
        if (!active) return;
        setFits({});
        setFitError(
          reason instanceof Error
            ? reason.message
            : "Opportunity-Fit konnte nicht geladen werden.",
        );
      })
      .finally(() => {
        if (active) setFitLoading(false);
      });
    return () => {
      active = false;
    };
  }, [items]);

  function toggleComparison(item: OpportunityListItem) {
    setComparisonError("");
    setSelectedItems((current) => {
      const existing = current.some((selected) => selected.id === item.id);
      if (existing)
        return current.filter((selected) => selected.id !== item.id);
      if (current.length >= 4) return current;
      return [...current, item];
    });
  }

  async function compareSelected() {
    if (selectedItems.length < 2 || selectedItems.length > 4) return;
    setComparisonLoading(true);
    setComparisonError("");
    try {
      const next = await api.compareOpportunities(
        selectedItems.map((item) => item.id),
      );
      setComparison(next);
    } catch (reason) {
      setComparisonError(
        reason instanceof Error
          ? reason.message
          : "Vergleich konnte nicht geladen werden.",
      );
    } finally {
      setComparisonLoading(false);
    }
  }

  if (comparison) {
    return (
      <OpportunityComparisonView
        comparison={comparison}
        onBack={() => setComparison(null)}
        onSelect={onSelect}
      />
    );
  }

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
        <label>
          Group/Wave
          <select
            aria-label="Group oder Wave filtern"
            value={groupFilter}
            onChange={(event) => setGroupFilter(event.target.value)}
          >
            <option value="">Alle Groups</option>
            {groups.map((group) => (
              <option key={group.id} value={group.id}>
                {group.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Sortierung
          <select
            aria-label="Opportunities sortieren"
            value={fitSort}
            onChange={(event) => setFitSort(event.target.value as FitSort)}
          >
            <option value="default">Standard</option>
            <option value="fit_desc">Bester Fit zuerst</option>
          </select>
        </label>
        <div className="view-toggle" aria-label="Opportunity Ansicht">
          <button
            type="button"
            className={displayMode === "list" ? "active" : ""}
            onClick={() => setDisplayMode("list")}
          >
            Liste
          </button>
          <button
            type="button"
            className={displayMode === "map" ? "active" : ""}
            onClick={() => setDisplayMode("map")}
          >
            Karte
          </button>
        </div>
      </header>
      {fitError && (
        <p className="muted" role="status">
          Fit nicht verfügbar: {fitError}
        </p>
      )}
      {selectedItems.length > 0 && (
        <section className="panel comparison-selection">
          <div className="comparison-selection-header">
            <div>
              <h2>Vergleichsauswahl</h2>
              <p>{selectedItems.length} von 2–4 Opportunities ausgewählt</p>
            </div>
            <div className="actions">
              <button type="button" onClick={() => setSelectedItems([])}>
                Auswahl löschen
              </button>
              <button
                className="primary"
                type="button"
                disabled={selectedItems.length < 2 || comparisonLoading}
                onClick={() => void compareSelected()}
              >
                {comparisonLoading ? "Vergleich wird geladen …" : "Vergleichen"}
              </button>
            </div>
          </div>
          <ol className="comparison-selection-list">
            {selectedItems.map((item) => (
              <li key={item.id}>
                <span>
                  {item.company_name} – {item.title}
                </span>
                <button type="button" onClick={() => toggleComparison(item)}>
                  Entfernen
                </button>
              </li>
            ))}
          </ol>
          {comparisonError && (
            <p className="state state-error" role="alert">
              {comparisonError}
            </p>
          )}
        </section>
      )}
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
      {displayMode === "list" ? (
        <div className="opportunity-grid">
          {visibleItems.map((item) => {
            const fit = fits[item.id];
            const expanded = expandedFitId === item.id;
            return (
              <article
                className={`opportunity-card status-${item.tracking_status}`}
                key={item.id}
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
                <span
                  className={`availability-badge availability-${availabilityOf(item)}`}
                >
                  {availabilityLabels[availabilityOf(item)]}
                </span>
                <small>{freshnessLabel(item)}</small>
                {item.groups && item.groups.length > 0 && (
                  <small className="group-membership-summary">
                    {item.groups.map((group) => group.name).join(" · ")}
                  </small>
                )}
                {fit ? (
                  <div className="record fit-card-summary">
                    <strong>
                      {fit.weighted_fit_score === null
                        ? "Fit offen"
                        : `Fit ${fit.weighted_fit_score}%`}
                    </strong>
                    <span>Evidenz {fit.evidence_completeness}%</span>
                    <small>
                      {hardStatusLabels[fit.hard_constraint_status]}
                    </small>
                    <button
                      type="button"
                      onClick={() => setExpandedFitId(expanded ? "" : item.id)}
                    >
                      {expanded ? "Fit-Erklärung schließen" : "Fit erklären"}
                    </button>
                  </div>
                ) : (
                  <small>
                    {fitLoading ? "Fit wird geladen …" : "Fit nicht verfügbar"}
                  </small>
                )}
                {expanded && fit && <OpportunityFitBreakdown fit={fit} />}
                <div className="opportunity-card-actions">
                  <label className="comparison-checkbox">
                    <input
                      type="checkbox"
                      aria-label={`Für Vergleich auswählen: ${item.company_name} – ${item.title}`}
                      checked={selectedItems.some(
                        (selected) => selected.id === item.id,
                      )}
                      disabled={
                        !selectedItems.some(
                          (selected) => selected.id === item.id,
                        ) && selectedItems.length >= 4
                      }
                      onChange={() => toggleComparison(item)}
                    />
                    Vergleich
                  </label>
                  <button type="button" onClick={() => onSelect(item.id)}>
                    Details
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <MapView visibleItems={visibleItems} onSelect={onSelect} />
      )}
    </section>
  );
}
