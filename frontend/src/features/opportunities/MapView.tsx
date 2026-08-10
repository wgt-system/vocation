import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import {
  api,
  type MapLocation,
  type MapProjectionFeature,
  type OpportunityListItem,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

const tileUrl =
  import.meta.env.VITE_MAP_TILE_URL ??
  "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const markerIcon = L.divIcon({
  className: "map-marker-icon",
  html: "",
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});
const precisionLabels: Record<string, string> = {
  exact_address: "Exakte Adresse",
  city: "Stadt",
  region: "Region",
  approximate: "Ungefähr",
};
const availabilityLabels = {
  available: "Verfügbar",
  unavailable: "Nicht verfügbar",
  uncertain: "Unsicher",
  unknown: "Unbekannt",
} as const;

type Draft = {
  query: string;
  latitude: string;
  longitude: string;
  resolved_query: string;
};

function precisionLabel(precision: string) {
  return precisionLabels[precision] ?? precision;
}

function FitBounds({ features }: { features: MapProjectionFeature[] }) {
  const map = useMap();
  useEffect(() => {
    if (features.length === 0) return;
    const bounds = L.latLngBounds(
      features.map((feature) => [feature.latitude, feature.longitude]),
    );
    map.fitBounds(bounds, { padding: [24, 24] });
  }, [features, map]);
  return null;
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
  const [mutationError, setMutationError] = useState("");
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
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

  return (
    <div className="map-workspace">
      {error && <ErrorState message={error} />}
      {mutationError && (
        <p className="state state-error" role="alert">
          {mutationError}
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
        <MapContainer
          className="opportunity-map"
          center={[51.1657, 10.4515]}
          zoom={6}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url={tileUrl}
          />
          <FitBounds features={features} />
          {features.map((feature) => (
            <Marker
              key={feature.feature_id}
              position={[feature.latitude, feature.longitude]}
              icon={markerIcon}
            >
              <Popup>
                <div className="map-popup">
                  <strong>{feature.title}</strong>
                  <span>{feature.company_name}</span>
                  <span>{feature.location_label}</span>
                  <span>Precision: {precisionLabel(feature.precision)}</span>
                  <span>Status: {feature.tracking_status}</span>
                  <span>
                    Availability: {availabilityLabels[feature.availability]}
                  </span>
                  {feature.groups.length > 0 && (
                    <span>
                      Groups/Waves:{" "}
                      {feature.groups.map((group) => group.name).join(" · ")}
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => onSelect(feature.opportunity_id)}
                  >
                    Details
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
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
