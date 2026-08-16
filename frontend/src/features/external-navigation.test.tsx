import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type ExternalLink,
  type MapProjectionFeature,
  type OpportunityDetail,
  type OpportunityListItem,
} from "../api/client";
import { OpportunityDetailView } from "./opportunities/OpportunityDetailView";
import { MapView } from "./opportunities/MapView";

vi.mock("../api/client", () => ({
  api: {
    getOpportunity: vi.fn(),
    listCriteria: vi.fn(),
    listExternalLinks: vi.fn(),
    listApplicationCases: vi.fn(),
    listApplicationMaterials: vi.fn(),
    getApplicationDocumentForMaterialRevision: vi.fn(),
    attachApplicationDocument: vi.fn(),
    openExternalLink: vi.fn(),
    listMapLocations: vi.fn(),
    getMapProjection: vi.fn(),
  },
}));

const links: ExternalLink[] = [
  {
    source_id: "source-1",
    source_name: "Acme Careers",
    source_type: "company_careers",
    posting_id: "posting-1",
    display_label: "Backend Engineer",
    availability: "available",
    observed_at: "2026-08-10T10:00:00Z",
    preferred: true,
    url: "https://example.test/one",
  },
  {
    source_id: "source-2",
    source_name: "Job Board",
    source_type: "job_board",
    posting_id: "posting-2",
    display_label: null,
    availability: "uncertain",
    observed_at: "2026-08-09T10:00:00Z",
    preferred: false,
    url: "https://example.test/two",
  },
];

const detail: OpportunityDetail = {
  id: "opp-1",
  title: "Backend Engineer",
  company: { id: "company-1", name: "Acme GmbH" },
  locations: [],
  postings: [
    {
      id: "posting-1",
      title: "Backend Engineer",
      observed_at: "2026-08-10T10:00:00Z",
      published_at: null,
      availability: "available",
      source: { id: "source-1", name: "Acme Careers", type: "company_careers" },
      source_reference: {
        id: "reference-1",
        display_label: "Backend Engineer",
        observed_at: "2026-08-10T10:00:00Z",
        url: "https://example.test/one",
      },
    },
  ],
  sources: [],
  observations: [],
  assessments: [],
  external_assessments: [],
  personal_assessments: [],
  personal_assessment_history: [],
  decision_history: [],
  import_provenance: {
    import_id: "import-1",
    bundle_id: "bundle-1",
    fingerprint: "fingerprint",
    applied_at: "2026-08-10T09:00:00Z",
  },
  tracking_status: "new",
};

const mapItem: OpportunityListItem = {
  id: "opp-1",
  title: "Backend Engineer",
  company_name: "Acme GmbH",
  locations: [],
  posting_count: 1,
  assessment_count: 0,
  import_id: "import-1",
  imported_at: "2026-08-10T09:00:00Z",
  tracking_status: "new",
};

const mapFeature: MapProjectionFeature = {
  feature_id: "feature-1",
  work_location_id: "location-1",
  opportunity_id: "opp-1",
  company_id: "company-1",
  title: "Backend Engineer",
  company_name: "Acme GmbH",
  location_label: "Hamburg",
  latitude: 53.55,
  longitude: 10,
  precision: "city",
  tracking_status: "new",
  availability: "available",
  groups: [],
};

function emitOrientationAction(iframe: HTMLIFrameElement, actionRef: string) {
  window.dispatchEvent(
    new MessageEvent("message", {
      source: iframe.contentWindow,
      data: JSON.stringify({
        contract: "orientation.host-bridge",
        version: "1.0",
        type: "action.activated",
        payload: {
          featureRef: "feature-1",
          sourceRef: "vocation.map_projection",
          actionRef,
        },
      }),
    }),
  );
}

beforeEach(() => {
  vi.mocked(api.listCriteria).mockResolvedValue([]);
  vi.mocked(api.getOpportunity).mockResolvedValue(detail);
  vi.mocked(api.listExternalLinks).mockResolvedValue(links);
  vi.mocked(api.listApplicationCases).mockResolvedValue([]);
  vi.mocked(api.listApplicationMaterials).mockResolvedValue([]);
  vi.mocked(api.getApplicationDocumentForMaterialRevision).mockResolvedValue(
    null,
  );
  vi.mocked(api.openExternalLink).mockResolvedValue(links[0]);
  vi.mocked(api.listMapLocations).mockResolvedValue([]);
  vi.mocked(api.getMapProjection).mockResolvedValue([mapFeature]);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("External navigation UI", () => {
  it("renders candidates, preferred marker, default and explicit actions", async () => {
    const user = userEvent.setup();
    render(<OpportunityDetailView opportunityId="opp-1" onBack={vi.fn()} />);
    expect(await screen.findByText("Acme Careers")).toBeInTheDocument();
    expect(screen.getByText(/bevorzugt/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Bevorzugte/ }));
    expect(api.openExternalLink).toHaveBeenCalledWith("opp-1", undefined);
    await user.click(screen.getAllByRole("button", { name: "Öffnen" })[1]);
    expect(api.openExternalLink).toHaveBeenCalledWith("opp-1", "posting-2");
  });

  it("shows the no-link state and keeps detail visible after open failure", async () => {
    vi.mocked(api.listExternalLinks).mockResolvedValueOnce([]);
    const user = userEvent.setup();
    render(<OpportunityDetailView opportunityId="opp-1" onBack={vi.fn()} />);
    expect(
      await screen.findByText("Keine gültige Originalanzeige verfügbar"),
    ).toBeInTheDocument();

    cleanup();
    vi.mocked(api.listExternalLinks).mockResolvedValue(links);
    render(<OpportunityDetailView opportunityId="opp-1" onBack={vi.fn()} />);
    await screen.findByText("Acme Careers");
    vi.mocked(api.openExternalLink).mockRejectedValueOnce(
      new Error("Browser konnte nicht geöffnet werden"),
    );
    await user.click(screen.getByRole("button", { name: /Bevorzugte/ }));
    expect(
      await screen.findByText("Browser konnte nicht geöffnet werden"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Backend Engineer", level: 1 }),
    ).toBeInTheDocument();
  });

  it("uses Vocation External Links for Orientation map actions instead of projection URLs", async () => {
    render(<MapView visibleItems={[mapItem]} onSelect={vi.fn()} />);
    const iframe = (await screen.findByTitle(
      "Vocation Opportunities map",
    )) as HTMLIFrameElement;

    await waitFor(() =>
      expect(api.listExternalLinks).toHaveBeenCalledWith("opp-1"),
    );

    emitOrientationAction(iframe, "open-preferred");
    await waitFor(() =>
      expect(api.openExternalLink).toHaveBeenCalledWith("opp-1", undefined),
    );

    emitOrientationAction(iframe, "open-posting:posting-2");
    await waitFor(() =>
      expect(api.openExternalLink).toHaveBeenCalledWith("opp-1", "posting-2"),
    );

    expect(
      screen.queryByText("https://example.test/one"),
    ).not.toBeInTheDocument();
  });
});
