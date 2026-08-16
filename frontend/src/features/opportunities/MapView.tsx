import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  api,
  type ExternalLink,
  type MapLocation,
  type MapProjectionFeature,
  type OpportunityListItem,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";
import {
  OrientationMapFrame,
  type OrientationMapAction,
} from "./OrientationMapFrame";

const precisionLabels: Record<string, string> = {
  exact_address: "Exakte Adresse",
  site: "Standort",
  city: "Stadt",
  region: "Region",
  approximate: "Ungefähr",
  unknown: "Unbekannt",
};

type Draft = {
  query: string;
  latitude: string;
  longitude: string;
  resolved_query: string;
};

function precisionLabel(precision: string) {
  return precisionLabels[precision] ?? precision;
}

function locationText(location: MapLocation) {
  return [location.city, location.region, location.country_code]
    .filter(Boolean)
    .join(" · ");
}

export function MapView({
  visibleItems,
  onSelect,
}: {
  visibleItems: OpportunityListItem[];
  onSelect: (id: string) => void;
}) {
  const [features, setFeatures] = useState<MapProjectionFeature[]>([]);
  const [locations, setLocations] = useState<MapLocation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mapHostError, setMapHostError] = useState("");
  const [mutationError, setMutationError] = useState("");
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [externalLinksByOpportunity, setExternalLinksByOpportunity] = useState<
    Record<string, ExternalLink[]>
  >({});
  const [externalLinksLoaded, setExternalLinksLoaded] = useState<Set<string>>(
    new Set(),
  );
  const [externalLinkErrors, setExternalLinkErrors] = useState<
    Record<string, string>
  >({});
  const [openingExternalLink, setOpeningExternalLink] = useState("");
  const externalLinkCache = useRef<Record<string, ExternalLink[]>>({});
  const externalLinkRequests = useRef(new Set<string>());
  const visibleOpportunityIds = useMemo(
    () => visibleItems.map((item) => item.id),
    [visibleItems],
  );
  const visibleKey = visibleOpportunityIds.join("\u0000");

  async function refreshData(opportunityIds: string[]) {
    const [nextLocations, nextFeatures] = await Promise.all([
      api.listMapLocations(),
      api.getMapProjection(opportunityIds),
    ]);
    setLocations(nextLocations);
    setFeatures(nextFeatures);
  }

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setMapHostError("");
    setFeatures([]);
    Promise.all([
      api.listMapLocations(),
      api.getMapProjection(visibleOpportunityIds),
    ])
      .then(([nextLocations, nextFeatures]) => {
        if (!active) return;
        setLocations(nextLocations);
        setFeatures(nextFeatures);
      })
      .catch((reason) => {
        if (active) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Karte konnte nicht geladen werden.",
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [visibleKey]);

  useEffect(() => {
    const opportunityIds = [
      ...new Set(features.map((feature) => feature.opportunity_id)),
    ];
    const pendingIds = opportunityIds.filter(
      (id) =>
        !externalLinkCache.current[id] && !externalLinkRequests.current.has(id),
    );
    pendingIds.forEach((id) => externalLinkRequests.current.add(id));
    if (pendingIds.length === 0) return;
    Promise.all(
      pendingIds.map(async (id) => {
        try {
          const links = await api.listExternalLinks(id);
          externalLinkCache.current[id] = links;
          setExternalLinksByOpportunity((current) => ({
            ...current,
            [id]: links,
          }));
          setExternalLinkErrors((current) => ({ ...current, [id]: "" }));
        } catch (reason) {
          setExternalLinkErrors((current) => ({
            ...current,
            [id]:
              reason instanceof Error
                ? reason.message
                : "Originalanzeigen konnten nicht geladen werden.",
          }));
        } finally {
          setExternalLinksLoaded((current) => new Set(current).add(id));
          externalLinkRequests.current.delete(id);
        }
      }),
    ).catch(() => undefined);
  }, [features]);

  const visibleLocationIds = new Set(visibleOpportunityIds);
  const visibleLocations = locations.filter((location) =>
    visibleLocationIds.has(location.opportunity_id),
  );

  function draftFor(location: MapLocation): Draft {
    return (
      drafts[location.work_location_id] ?? {
        query: location.label,
        latitude: location.resolution?.latitude.toString() ?? "",
        longitude: location.resolution?.longitude.toString() ?? "",
        resolved_query: location.resolution?.resolved_query ?? location.label,
      }
    );
  }

  function updateDraft(id: string, changes: Partial<Draft>) {
    const location = locations.find((item) => item.work_location_id === id);
    if (!location) return;
    setDrafts((current) => ({
      ...current,
      [id]: { ...draftFor(location), ...changes },
    }));
  }

  async function mutateLocation(
    workLocationId: string,
    operation: () => Promise<unknown>,
  ) {
    setMutationError("");
    try {
      await operation();
      await refreshData(visibleOpportunityIds);
    } catch (reason) {
      setMutationError(
        reason instanceof Error
          ? reason.message
          : "Auflösung konnte nicht gespeichert werden.",
      );
    }
  }

  async function geocode(location: MapLocation) {
    const draft = draftFor(location);
    if (!draft.query.trim()) {
      setMutationError("Bitte eine Geocode-Suchanfrage eingeben.");
      return;
    }
    await mutateLocation(location.work_location_id, () =>
      api.geocodeMapLocation(location.work_location_id, {
        query: draft.query.trim(),
      }),
    );
  }

  async function saveManual(location: MapLocation) {
    const draft = draftFor(location);
    const latitude = Number(draft.latitude);
    const longitude = Number(draft.longitude);
    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      !draft.resolved_query.trim()
    ) {
      setMutationError(
        "Latitude, Longitude und aufgelöste Bezeichnung sind erforderlich.",
      );
      return;
    }
    await mutateLocation(location.work_location_id, () =>
      api.setMapResolution(location.work_location_id, {
        latitude,
        longitude,
        resolved_query: draft.resolved_query.trim(),
      }),
    );
  }

  async function deleteResolution(location: MapLocation) {
    await mutateLocation(location.work_location_id, () =>
      api.deleteMapResolution(location.work_location_id),
    );
  }

  const handleMapAction = useCallback(
    async (action: OrientationMapAction) => {
      if (action.kind === "details") {
        onSelect(action.opportunityId);
        return;
      }

      const key = `${action.opportunityId}:${action.postingId ?? "preferred"}`;
      setOpeningExternalLink(key);
      setExternalLinkErrors((current) => ({
        ...current,
        [action.opportunityId]: "",
      }));
      try {
        await api.openExternalLink(action.opportunityId, action.postingId);
      } catch (reason) {
        setExternalLinkErrors((current) => ({
          ...current,
          [action.opportunityId]:
            reason instanceof Error
              ? reason.message
              : "Originalanzeige konnte nicht geöffnet werden.",
        }));
      } finally {
        setOpeningExternalLink("");
      }
    },
    [onSelect],
  );

  return (
    <div className="map-workspace">
      {error && <ErrorState message={error} />}
      {mutationError && (
        <p className="state state-error" role="alert">
          {mutationError}
        </p>
      )}
      {mapHostError && (
        <p className="state state-error" role="alert">
          {mapHostError}
        </p>
      )}
      {openingExternalLink && (
        <p className="state" role="status">
          Originalanzeige wird geöffnet …
        </p>
      )}
      {loading && <Loading label="Karte wird geladen …" />}
      {!loading && features.length === 0 && (
        <EmptyState>
          <h2>Keine aufgelösten WorkLocations</h2>
          <p>
            Für die aktuell sichtbaren Opportunities gibt es noch keine
            Kartenposition.
          </p>
        </EmptyState>
      )}
      {features.length > 0 && (
        <OrientationMapFrame
          features={features}
          externalLinksByOpportunity={externalLinksByOpportunity}
          externalLinksLoaded={externalLinksLoaded}
          externalLinkErrors={externalLinkErrors}
          onAction={(action) => void handleMapAction(action)}
          onHostError={setMapHostError}
        />
      )}

      <section className="panel map-locations-panel">
        <h2>Location-Auflösungen</h2>
        {visibleLocations.length === 0 ? (
          <p>Keine WorkLocations für die aktuelle Auswahl.</p>
        ) : (
          <div className="map-location-list">
            {visibleLocations.map((location) => {
              const draft = draftFor(location);
              return (
                <article
                  className="map-location-card"
                  key={location.work_location_id}
                >
                  <div>
                    <strong>{location.title}</strong>
                    <small>
                      {location.company_name} · {location.label}
                    </small>
                    {locationText(location) && (
                      <small>{locationText(location)}</small>
                    )}
                    <small>
                      Precision: {precisionLabel(location.precision)}
                    </small>
                    {location.resolution ? (
                      <small>
                        {location.resolution.resolution_source} ·{" "}
                        {location.resolution.latitude},{" "}
                        {location.resolution.longitude}
                      </small>
                    ) : (
                      <small>Unmapped</small>
                    )}
                  </div>
                  <div className="map-resolution-controls">
                    <label>
                      Geocode Query
                      <input
                        value={draft.query}
                        onChange={(event) =>
                          updateDraft(location.work_location_id, {
                            query: event.target.value,
                          })
                        }
                      />
                    </label>
                    <button
                      type="button"
                      onClick={() => void geocode(location)}
                    >
                      Geocodieren
                    </button>
                    <div className="map-manual-fields">
                      <label>
                        Latitude
                        <input
                          inputMode="decimal"
                          value={draft.latitude}
                          onChange={(event) =>
                            updateDraft(location.work_location_id, {
                              latitude: event.target.value,
                            })
                          }
                        />
                      </label>
                      <label>
                        Longitude
                        <input
                          inputMode="decimal"
                          value={draft.longitude}
                          onChange={(event) =>
                            updateDraft(location.work_location_id, {
                              longitude: event.target.value,
                            })
                          }
                        />
                      </label>
                    </div>
                    <label>
                      Aufgelöste Bezeichnung
                      <input
                        value={draft.resolved_query}
                        onChange={(event) =>
                          updateDraft(location.work_location_id, {
                            resolved_query: event.target.value,
                          })
                        }
                      />
                    </label>
                    <div className="actions">
                      <button
                        type="button"
                        onClick={() => void saveManual(location)}
                      >
                        Manuell speichern
                      </button>
                      {location.resolution && (
                        <button
                          type="button"
                          onClick={() => void deleteResolution(location)}
                        >
                          Auflösung löschen
                        </button>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
