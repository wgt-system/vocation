import type { ReactNode } from "react";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type MapLocation,
  type MapProjectionFeature,
  type OpportunityListItem,
} from "../api/client";
import { OpportunityList } from "./opportunities/OpportunityList";
import { MapView } from "./opportunities/MapView";

vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }: { children: ReactNode }) => (
    <div>{children}</div>
  ),
  TileLayer: () => null,
  Popup: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  Marker: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  useMap: () => ({ fitBounds: vi.fn() }),
}));

vi.mock("../api/client", () => ({
  api: {
    listOpportunities: vi.fn(),
    listGroups: vi.fn(),
    listMapLocations: vi.fn(),
    getMapProjection: vi.fn(),
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
    provider_key: "nominatim",
    resolution_source: "geocoder",
    resolved_at: "2026-08-10T10:00:00Z",
    resolved_query: "Hamburg",
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

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([]);
  vi.mocked(api.listMapLocations).mockResolvedValue([location]);
  vi.mocked(api.getMapProjection).mockResolvedValue([feature]);
  vi.mocked(api.geocodeMapLocation).mockResolvedValue(location.resolution!);
  vi.mocked(api.setMapResolution).mockResolvedValue(location.resolution!);
  vi.mocked(api.deleteMapResolution).mockResolvedValue(undefined);
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
    await screen.findAllByText("Engineer");
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
    const onSelect = vi.fn();
    render(
      <MapView
        visibleItems={[opportunity("opp-1", "Engineer", "new", "available")]}
        onSelect={onSelect}
      />,
    );
    await screen.findByRole("button", { name: "Details" });
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

  it("opens the existing Opportunity detail flow from a feature popup", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <MapView
        visibleItems={[opportunity("opp-1", "Engineer", "new", "available")]}
        onSelect={onSelect}
      />,
    );
    await user.click(await screen.findByRole("button", { name: "Details" }));
    expect(onSelect).toHaveBeenCalledWith("opp-1");
  });
});
