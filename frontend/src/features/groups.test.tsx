import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  api,
  type OpportunityGroup,
  type OpportunityListItem,
} from "../api/client";
import { OpportunityList } from "./opportunities/OpportunityList";
import { GroupsView } from "./groups/GroupsView";

vi.mock("../api/client", () => ({
  api: {
    listGroups: vi.fn(),
    getGroup: vi.fn(),
    createGroup: vi.fn(),
    editGroup: vi.fn(),
    deleteGroup: vi.fn(),
    addGroupMembership: vi.fn(),
    removeGroupMembership: vi.fn(),
    reorderGroup: vi.fn(),
    listOpportunities: vi.fn(),
  },
}));

const opportunity = (id: string, title: string): OpportunityListItem => ({
  id,
  title,
  company_name: "Acme GmbH",
  locations: [],
  posting_count: 1,
  assessment_count: 0,
  import_id: "import-1",
  imported_at: "2026-08-09T10:00:00Z",
  tracking_status: "new",
});

function groupFixture(
  memberships = [
    {
      company_name: "Acme GmbH",
      opportunity_id: "opp-1",
      opportunity_title: "First role",
      position: 0,
    },
    {
      company_name: "Acme GmbH",
      opportunity_id: "opp-2",
      opportunity_title: "Second role",
      position: 1,
    },
  ],
): OpportunityGroup {
  return {
    id: "group-1",
    name: "Applications",
    description: "Current applications",
    group_type: "application_wave",
    memberships,
  };
}

beforeEach(() => {
  vi.mocked(api.listGroups).mockResolvedValue([groupFixture()]);
  vi.mocked(api.listOpportunities).mockResolvedValue([
    opportunity("opp-1", "First role"),
    opportunity("opp-2", "Second role"),
    opportunity("opp-3", "Third role"),
  ]);
  vi.mocked(api.getGroup).mockResolvedValue(groupFixture());
  vi.mocked(api.createGroup).mockResolvedValue(groupFixture([]));
  vi.mocked(api.editGroup).mockResolvedValue(groupFixture([]));
  vi.mocked(api.deleteGroup).mockResolvedValue(undefined);
  vi.mocked(api.addGroupMembership).mockResolvedValue(groupFixture());
  vi.mocked(api.removeGroupMembership).mockResolvedValue(
    groupFixture([
      {
        company_name: "Acme GmbH",
        opportunity_id: "opp-2",
        opportunity_title: "Second role",
        position: 0,
      },
    ]),
  );
  vi.mocked(api.reorderGroup).mockResolvedValue(groupFixture());
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Groups & Waves workflow", () => {
  it("creates, edits and explicitly deletes a Group", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();
    render(<GroupsView />);

    await user.clear(await screen.findByLabelText("Name"));
    await user.type(screen.getByLabelText("Name"), "Research shortlist");
    await user.click(screen.getByRole("button", { name: "Group erstellen" }));
    expect(api.createGroup).toHaveBeenCalledWith({
      name: "Research shortlist",
      description: "",
      group_type: "general",
    });

    await user.click(await screen.findByRole("button", { name: "Bearbeiten" }));
    await user.clear(screen.getByLabelText("Name"));
    await user.type(screen.getByLabelText("Name"), "Edited shortlist");
    await user.click(screen.getByRole("button", { name: "Speichern" }));
    expect(api.editGroup).toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Löschen" }));
    expect(window.confirm).toHaveBeenCalled();
    expect(api.deleteGroup).toHaveBeenCalledWith("group-1");
  });

  it("adds, removes and reorders memberships", async () => {
    const user = userEvent.setup();
    render(<GroupsView />);
    await user.click(
      await screen.findByRole("button", { name: /Applications/ }),
    );

    await user.selectOptions(
      screen.getByLabelText("Opportunity zur Group hinzufügen"),
      "opp-3",
    );
    await user.click(screen.getByRole("button", { name: "Hinzufügen" }));
    expect(api.addGroupMembership).toHaveBeenCalledWith("group-1", "opp-3");

    await user.click(
      screen.getByRole("button", { name: "First role nach unten" }),
    );
    expect(api.reorderGroup).toHaveBeenCalledWith("group-1", [
      "opp-2",
      "opp-1",
    ]);

    await user.click(screen.getAllByRole("button", { name: "Entfernen" })[0]);
    expect(api.removeGroupMembership).toHaveBeenCalledWith("group-1", "opp-1");
  });

  it("filters Opportunities through the backend group_id filter", async () => {
    const user = userEvent.setup();
    render(<OpportunityList refreshToken={0} onSelect={vi.fn()} />);
    await screen.findByText("First role");
    await user.selectOptions(
      screen.getByLabelText("Group oder Wave filtern"),
      "group-1",
    );
    expect(api.listOpportunities).toHaveBeenLastCalledWith("group-1");
  });
});
