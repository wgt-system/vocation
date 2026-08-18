import { useState } from "react";

import { OpportunityDetailView } from "./features/opportunities/OpportunityDetailView";
import { OpportunityDetailFitPanel } from "./features/opportunities/OpportunityFitBreakdown";
import { OpportunityList } from "./features/opportunities/OpportunityList";
import { OpportunityNotePanel } from "./features/opportunities/OpportunityNotePanel";
import { ProfileSearchView } from "./features/profiles/ProfileSearchView";
import { PromptView } from "./features/prompts/PromptView";
import { OrganisationView } from "./features/workspace/OrganisationView";
import { ToolsView } from "./features/workspace/ToolsView";

type PrimaryView = "market" | "profile" | "research" | "applications";
type View = PrimaryView | "tools";

const primaryLabels: Record<PrimaryView, string> = {
  market: "Stellenmarkt",
  profile: "Profile",
  research: "Recherche",
  applications: "Bewerbungen",
};

export default function App() {
  const [view, setView] = useState<View>("market");
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(
    null,
  );
  const [refreshToken, setRefreshToken] = useState(0);

  function navigate(next: View) {
    setView(next);
    setSelectedOpportunity(null);
  }

  function markImported() {
    setRefreshToken((value) => value + 1);
  }

  function finishResearchImport() {
    markImported();
    navigate("market");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span>V</span>
          <div>
            <strong>Vocation</strong>
            <small>Qualitative Jobsuche</small>
          </div>
        </div>
        <nav aria-label="Arbeitsbereiche">
          <small className="nav-section-label">Arbeitsbereiche</small>
          {(Object.keys(primaryLabels) as PrimaryView[]).map((item) => (
            <button
              className={view === item ? "active" : ""}
              key={item}
              onClick={() => navigate(item)}
            >
              {primaryLabels[item]}
            </button>
          ))}
          <small className="nav-section-label">Erweitert</small>
          <button
            className={view === "tools" ? "active" : ""}
            onClick={() => navigate("tools")}
          >
            Werkzeuge
          </button>
        </nav>
      </aside>
      <main className="content">
        {view === "market" &&
          (selectedOpportunity ? (
            <div className="page-stack">
              <OpportunityDetailFitPanel opportunityId={selectedOpportunity} />
              <OpportunityNotePanel opportunityId={selectedOpportunity} />
              <OpportunityDetailView
                opportunityId={selectedOpportunity}
                onBack={() => setSelectedOpportunity(null)}
              />
            </div>
          ) : (
            <OpportunityList
              refreshToken={refreshToken}
              onSelect={setSelectedOpportunity}
              onStartResearch={() => navigate("research")}
              onOpenProfiles={() => navigate("profile")}
            />
          ))}
        {view === "profile" && <ProfileSearchView />}
        {view === "research" && (
          <PromptView onImported={finishResearchImport} />
        )}
        {view === "applications" && <OrganisationView />}
        {view === "tools" && <ToolsView onImported={markImported} />}
      </main>
    </div>
  );
}
