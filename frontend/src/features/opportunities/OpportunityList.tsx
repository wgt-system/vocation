import { useEffect, useState } from "react";

import {
  api,
  type OpportunityComparison,
  type OpportunityGroup,
  type OpportunityListItem,
  type TrackingStatus,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";
import {
  profileApi,
  type SearchProfile,
} from "../profiles/profileApi";
import { fitApi, type OpportunityFit } from "./fitApi";
import { MapView } from "./MapView";
import { OpportunityComparisonView } from "./OpportunityComparisonView";
import { OpportunityFitBreakdown } from "./OpportunityFitBreakdown";
import {
  analyzeOpportunities,
  type Availability,
  type EvidenceFilter,
  type HardConstraintFilter,
  type OpportunitySort,
} from "./opportunityWorkspace";

type DisplayMode = "list" | "map";

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
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TrackingStatus[]>([]);
  const [availabilityFilter, setAvailabilityFilter] = useState<
    Availability | "all"
  >("all");
  const [hardConstraintFilter, setHardConstraintFilter] =
    useState<HardConstraintFilter>("all");
  const [evidenceFilter, setEvidenceFilter] =
    useState<EvidenceFilter>("all");
  const [sort, setSort] = useState<OpportunitySort>("recency_desc");
  const [groups, setGroups] = useState<OpportunityGroup[]>([]);
  const [groupFilter, setGroupFilter] = useState("");
  const [searchProfiles, setSearchProfiles] = useState<SearchProfile[]>([]);
  const [selectedSearchProfileId, setSelectedSearchProfileId] = useState("");
  const [profilesLoading, setProfilesLoading] = useState(true);
  const [profileError, setProfileError] = useState("");
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
  const visibleItems = analyzeOpportunities(items, fits, {
    query,
    statuses: statusFilter,
    availability: availabilityFilter,
    hardConstraint: hardConstraintFilter,
    evidence: evidenceFilter,
    sort,
  });
  const defaultSearchProfileId =
    searchProfiles.find((profile) => profile.is_default)?.id ??
    searchProfiles[0]?.id ??
    "";

  function toggleStatus(status: TrackingStatus) {
    setStatusFilter((current) =>
      current.includes(status)
        ? current.filter((item) => item !== status)
        : [...current, status],
    );
  }

  function resetWorkspace() {
    setQuery("");
    setStatusFilter([]);
    setAvailabilityFilter("all");
    setHardConstraintFilter("all");
    setEvidenceFilter("all");
    setSort("recency_desc");
    setGroupFilter("");
    setSelectedSearchProfileId(defaultSearchProfileId);
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
    setProfilesLoading(true);
    setProfileError("");
    profileApi
      .listSearchProfiles()
      .then((profiles) => {
        setSearchProfiles(profiles);
        setSelectedSearchProfileId((current) => {
          if (current && profiles.some((profile) => profile.id === current)) {
            return current;
          }
          return (
            profiles.find((profile) => profile.is_default)?.id ??
            profiles[0]?.id ??
            ""
          );
        });
      })
      .catch((reason) => {
        setSearchProfiles([]);
        setSelectedSearchProfileId("");
        setProfileError(
          reason instanceof Error
            ? reason.message
            : "Search Profiles konnten nicht geladen werden.",
        );
      })
      .finally(() => setProfilesLoading(false));
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
    if (!selectedSearchProfileId) {
      setFits({});
      setFitLoading(false);
      setFitError(
        profilesLoading || profileError
          ? ""
          : "Kein Search Profile für die Fit-Analyse verfügbar.",
      );
      return () => {
        active = false;
      };
    }
    setFitLoading(true);
    setFitError("");
    fitApi
      .list(
        items.map((item) => item.id),
        selectedSearchProfileId,
      )
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
  }, [items, profileError, profilesLoading, selectedSearchProfileId]);

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
        <span className="count-badge">
          {visibleItems.length} von {items.length}
        </span>
        <label>
          Suche
          <input
            type="search"
            aria-label="Opportunities durchsuchen"
            placeholder="Titel, Unternehmen oder Ort"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <label>
          Search Profile
          <select
            aria-label="Search Profile für Opportunity-Analyse"
            value={selectedSearchProfileId}
            disabled={profilesLoading || searchProfiles.length === 0}
            onChange={(event) => setSelectedSearchProfileId(event.target.value)}
          >
            {searchProfiles.length === 0 && (
              <option value="">Kein Search Profile</option>
            )}
            {searchProfiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
                {profile.is_default ? " (Standard)" : ""}
              </option>
            ))}
          </select>
        </label>
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
        </fieldset>
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
          Harte Kriterien
          <select
            aria-label="Harte Kriterien filtern"
            value={hardConstraintFilter}
            onChange={(event) =>
              setHardConstraintFilter(
                event.target.value as HardConstraintFilter,
              )
            }
          >
            <option value="all">Alle</option>
            <option value="pass">Erfüllt</option>
            <option value="fail">Nicht erfüllt</option>
            <option value="unknown">Offen</option>
          </select>
        </label>
        <label>
          Evidenz
          <select
            aria-label="Evidenz filtern"
            value={evidenceFilter}
            onChange={(event) =>
              setEvidenceFilter(event.target.value as EvidenceFilter)
            }
          >
            <option value="all">Alle</option>
            <option value="missing">Fehlende Evidenz</option>
            <option value="complete">Keine fehlende Evidenz</option>
          </select>
        </label>
        <label>
          Sortierung
          <select
            aria-label="Opportunities sortieren"
            value={sort}
            onChange={(event) => setSort(event.target.value as OpportunitySort)}
          >
            <option value="recency_desc">Neueste zuerst</option>
            <option value="fit_desc">Bester Fit zuerst</option>
            <option value="evidence_desc">Beste Evidenz zuerst</option>
            <option value="company_asc">Unternehmen A–Z</option>
            <option value="title_asc">Titel A–Z</option>
          </select>
        </label>
        <button type="button" onClick={resetWorkspace}>
          Analyse zurücksetzen
        </button>
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
      {profileError && (
        <p className="state state-error" role="alert">
          Search Profiles nicht verfügbar: {profileError}
        </p>
      )}
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
      {!loading && !error && items.length > 0 && visibleItems.length === 0 && (
        <EmptyState>
          <h2>Keine passenden Opportunities</h2>
          <p>Die aktuelle Suche oder Filterkombination liefert kein Ergebnis.</p>
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