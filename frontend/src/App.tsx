import { useState } from "react";

import { OpportunityDetailView } from "./features/opportunities/OpportunityDetailView";
import { OpportunityDetailFitPanel } from "./features/opportunities/OpportunityFitBreakdown";
import { OpportunityList } from "./features/opportunities/OpportunityList";
import { OpportunityNotePanel } from "./features/opportunities/OpportunityNotePanel";
import { ProfileSearchView } from "./features/profiles/ProfileSearchView";
import { PromptView } from "./features/prompts/PromptView";
import { OrganisationView } from "./features/workspace/OrganisationView";
import { ToolsView } from "./features/workspace/ToolsView";

type PrimaryView = "market" | "profile" | "research" | "organisation";
type View = PrimaryView | "tools";

const primaryLabels: Record<PrimaryView, string> = {
  market: "Stellenmarkt",
  profile: "Profil & Suche",
  research: "Recherche",
  organisation: "Organisation",
};

function WorkflowLinks({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section className="panel workflow-links" aria-label="Workflow-Navigation">
      <div>
        <p className="eyebrow">Nächster Schritt</p>
        <p className="muted">Wechsle direkt zum passenden Arbeitsbereich.</p>
      </div>
      <div className="actions">{children}</div>
    </section>
  );
}

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
          <small className="nav-section-label">Arbeitsbereich</small>
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
        <p className="local-note">Lokal · privat · nachvollziehbar</p>
      </aside>
      <main className="content">
        {view === "market" &&
          (selectedOpportunity ? (
            <>
              <OpportunityDetailFitPanel opportunityId={selectedOpportunity} />
              <OpportunityNotePanel opportunityId={selectedOpportunity} />
              <OpportunityDetailView
                opportunityId={selectedOpportunity}
                onBack={() => setSelectedOpportunity(null)}
              />
            </>
          ) : (
            <>
              <WorkflowLinks>
                <button type="button" onClick={() => navigate("profile")}>
                  Profil konfigurieren
                </button>
                <button
                  className="primary"
                  type="button"
                  onClick={() => navigate("research")}
                >
                  Recherche starten
                </button>
              </WorkflowLinks>
              <OpportunityList
                refreshToken={refreshToken}
                onSelect={setSelectedOpportunity}
              />
            </>
          ))}
        {view === "profile" && (
          <>
            <WorkflowLinks>
              <button type="button" onClick={() => navigate("market")}>
                Zum Stellenmarkt
              </button>
              <button
                className="primary"
                type="button"
                onClick={() => navigate("research")}
              >
                Mit Profil recherchieren
              </button>
            </WorkflowLinks>
            <ProfileSearchView />
          </>
        )}
        {view === "research" && (
          <>
            <WorkflowLinks>
              <button type="button" onClick={() => navigate("profile")}>
                Profil prüfen
              </button>
              <button
                className="primary"
                type="button"
                onClick={() => navigate("market")}
              >
                Stellenmarkt öffnen
              </button>
            </WorkflowLinks>
            <PromptView onImported={markImported} />
          </>
        )}
        {view === "organisation" && <OrganisationView />}
        {view === "tools" && <ToolsView onImported={markImported} />}
      </main>
    </div>
  );
}
