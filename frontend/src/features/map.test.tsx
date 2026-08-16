import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type ExternalLink,
  type MapLocation,
  type MapProjectionFeature,
  type OpportunityListItem,
} from "../api/client";
import { OpportunityList } from "./opportunities/OpportunityList";
import {
  buildOrientationScene,
  OrientationMapFrame,
} from "./opportunities/OrientationMapFrame";
import { MapView } from "./opportunities/MapView";

vi.mock("../api/client", () => ({
  api: {
    listOpportunities: vi.fn(),
    listGroups: vi.fn(),
    listMapLocations: vi.fn(),
    getMapProjection: vi.fn(),
    listExternalLinks: vi.fn(),
    openExternalLink: vi.fn(),
    geocodeMapLocation: vi.fn(),
    setMapResolution: vi.fn(),
    deleteMapResolution: vi.fn(),
  },
}));

const opportunity = (
  id: string,
  title: string,
  tracking_status: OpportunityListItem["tracking_status"],
  availability: NonNullable<OpportunityListItem["availability"]>,
): OpportunityListItem => ({
  id,
  title,
  company_name: "Acme GmbH",
  locations: [],
  posting_count: 1,
  assessment_count: 0,
  import_id: "import-1",
  imported_at: "2026-08-10T10:00:00Z",
  tracking_status,
  availability,
});

const location: MapLocation = {
  work_location_id: "location-1",
  opportunity_id: "opp-1",
  title: "Engineer",
  company_id: "company-1",
  company_name: "Acme GmbH",
  label: "Hamburg",
  city: "Hamburg",
  region: "Hamburg",
  country_code: "DE",
  precision: "city",
  resolution: {
    latitude: 53.55,
    longitude: 10,
    provider_key: "photon:city:123",
    resolution_source: "geocoder",
    resolved_at: "2026-08-10T10:00:00Z",
    resolved_query: "Hamburg, Deutschland",
  },
};

const feature: MapProjectionFeature = {
  feature_id: "feature-1",
  work_location_id: "location-1",
  opportunity_id: "opp-1",
  company_id: "company-1",
  title: "Engineer",
  company_name: "Acme GmbH",
  location_label: "Hamburg",
  latitude: 53.55,
  longitude: 10,
  precision: "city",
  tracking_status: "new",
  availability: "available",
  groups: [],
};

function emitBridgeMessage(
  iframe: HTMLIFrameElement,
  type: string,
  payload: Record<string, unknown>,
  origin = window.location.origin,
) {
  window.dispatchEvent(
    new MessageEvent("message", {
      source: iframe.contentWindow,
      origin,
      data: JSON.stringify({
        contract: "orientation.host-bridge",
        version: "1.0",
        type,
        payload,
      }),
    }),
  );
}

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([]);
  vi.mocked(api.listMapLocations).mockResolvedValue([location]);
  vi.mocked(api.getMapProjection).mockResolvedValue([feature]);
  vi.mocked(api.geocodeMapLocation).mockResolvedValue(location.resolution!);
  vi.mocked(api.setMapResolution).mockResolvedValue(location.resolution!);
  vi.mocked(api.deleteMapResolution).mockResolvedValue(undefined);
  vi.mocked(api.listExternalLinks).mockResolvedValue([]);
  vi.mocked(api.openExternalLink).mockResolvedValue({} as ExternalLink);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("desktop map workflow", () => {
  it("sends exactly the currently visible filtered Opportunity IDs", async () => {
    vi.mocked(api.listOpportunities).mockResolvedValue([
      opportunity("opp-1", "Visible", "new", "available"),
      opportunity("opp-2", "Excluded by status", "excluded", "available"),
      opportunity("opp-3", "Excluded by availability", "new", "unavailable"),
    ]);
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    await screen.findByText("Visible");
    await user.click(screen.getByRole("checkbox", { name: "Neu" }));
    await user.click(screen.getByRole("button", { name: "Karte" }));
    await screen.findByTitle("Vocation Opportunities map");
    await user.selectOptions(
      screen.getByLabelText("Availability filtern"),
      "available",
    );
    await waitFor(() =>
      expect(api.getMapProjection).toHaveBeenLastCalledWith(["opp-1"]),
    );
  });

  it("refreshes projection after explicit geocode, manual save and delete", async () => {
    const user = userEvent.setup();
    render(
      <MapView
        visibleItems={[opportunity("opp-1", "Engineer", "new", "available")]}
        onSelect={vi.fn()}
      />,
    );
    await screen.findByTitle("Vocation Opportunities map");
    expect(api.getMapProjection).toHaveBeenCalledWith(["opp-1"]);
    await user.click(screen.getByRole("button", { name: "Geocodieren" }));
    expect(api.geocodeMapLocation).toHaveBeenCalledWith("location-1", {
      query: "Hamburg",
    });
    expect(api.getMapProjection).toHaveBeenCalledTimes(2);

    await user.clear(screen.getByLabelText("Latitude"));
    await user.type(screen.getByLabelText("Latitude"), "53.56");
    await user.click(screen.getByRole("button", { name: "Manuell speichern" }));
    expect(api.setMapResolution).toHaveBeenCalled();
    expect(api.getMapProjection).toHaveBeenCalledTimes(3);

    await user.click(screen.getByRole("button", { name: "Auflösung löschen" }));
    expect(api.deleteMapResolution).toHaveBeenCalledWith("location-1");
    expect(api.getMapProjection).toHaveBeenCalledTimes(4);
  });

  it("routes Orientation detail actions into the existing Opportunity detail flow", async () => {
    const onSelect = vi.fn();
    render(
      <MapView
        visibleItems={[opportunity("opp-1", "Engineer", "new", "available")]}
        onSelect={onSelect}
      />,
    );
    const iframe = (await screen.findByTitle(
      "Vocation Opportunities map",
    )) as HTMLIFrameElement;

    emitBridgeMessage(iframe, "action.activated", {
      featureRef: "feature-1",
      sourceRef: "vocation.map_projection",
      actionRef: "details",
    });

    await waitFor(() => expect(onSelect).toHaveBeenCalledWith("opp-1"));
  });
});

describe("Orientation map boundary", () => {
  it("maps Vocation semantics into provider-neutral SpatialScene content", () => {
    const links = [
      {
        posting_id: "posting-1",
        source_name: "Example Jobs",
        display_label: "Original",
      } as ExternalLink,
      {
        posting_id: "posting-2",
        source_name: "Company",
        display_label: null,
      } as ExternalLink,
    ];

    const scene = buildOrientationScene(
      [feature],
      { "opp-1": links },
      new Set(["opp-1"]),
      {},
    );

    expect(scene.features).toEqual([
      expect.objectContaining({
        ref: "feature-1",
        sourceRef: "vocation.map_projection",
        coordinate: { longitude: 10, latitude: 53.55 },
        title: "Engineer",
        subtitle: "Acme GmbH · Hamburg",
      }),
    ]);
    expect(scene.features[0]?.information[0]?.rows).toEqual(
      expect.arrayContaining([
        { label: "Company", value: "Acme GmbH" },
        { label: "Location", value: "Hamburg" },
        { label: "Precision", value: "Stadt" },
        { label: "Availability", value: "Verfügbar" },
      ]),
    );
    expect(scene.features[0]?.actions).toEqual([
      { ref: "details", label: "Details" },
      { ref: "open-preferred", label: "Originalanzeige öffnen" },
      {
        ref: "open-posting:posting-1",
        label: "Quelle öffnen · Example Jobs · Original",
      },
      { ref: "open-posting:posting-2", label: "Quelle öffnen · Company" },
    ]);
  });

  it("accepts bridge events only from its own same-origin Orientation iframe", async () => {
    const onAction = vi.fn();
    render(
      <OrientationMapFrame
        features={[feature]}
        externalLinksByOpportunity={{}}
        externalLinksLoaded={new Set(["opp-1"])}
        externalLinkErrors={{}}
        onAction={onAction}
        onHostError={vi.fn()}
      />,
    );
    const iframe = screen.getByTitle(
      "Vocation Opportunities map",
    ) as HTMLIFrameElement;

    window.dispatchEvent(
      new MessageEvent("message", {
        source: window,
        origin: window.location.origin,
        data: JSON.stringify({
          contract: "orientation.host-bridge",
          version: "1.0",
          type: "action.activated",
          payload: {
            featureRef: "feature-1",
            sourceRef: "vocation.map_projection",
            actionRef: "details",
          },
        }),
      }),
    );
    expect(onAction).not.toHaveBeenCalled();

    emitBridgeMessage(
      iframe,
      "action.activated",
      {
        featureRef: "feature-1",
        sourceRef: "vocation.map_projection",
        actionRef: "details",
      },
      "https://attacker.invalid",
    );
    expect(onAction).not.toHaveBeenCalled();

    emitBridgeMessage(iframe, "action.activated", {
      featureRef: "feature-1",
      sourceRef: "vocation.map_projection",
      actionRef: "details",
    });
    await waitFor(() =>
      expect(onAction).toHaveBeenCalledWith({
        opportunityId: "opp-1",
        kind: "details",
      }),
    );
  });

  it("sends scene.replace only to the iframe's same origin", async () => {
    render(
      <OrientationMapFrame
        features={[feature]}
        externalLinksByOpportunity={{}}
        externalLinksLoaded={new Set(["opp-1"])}
        externalLinkErrors={{}}
        onAction={vi.fn()}
        onHostError={vi.fn()}
      />,
    );
    const iframe = screen.getByTitle(
      "Vocation Opportunities map",
    ) as HTMLIFrameElement;
    const postMessage = vi.spyOn(iframe.contentWindow!, "postMessage");

    emitBridgeMessage(iframe, "bridge.ready", {});

    await waitFor(() => expect(postMessage).toHaveBeenCalled());
    expect(postMessage.mock.calls.at(-1)?.[1]).toBe(window.location.origin);
  });
});
