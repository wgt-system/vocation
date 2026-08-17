import { useState } from "react";

import { CriteriaView } from "./features/criteria/CriteriaView";
import { DuplicateCasesView } from "./features/duplicates/DuplicateCasesView";
import { GroupsView } from "./features/groups/GroupsView";
import { ImportView } from "./features/imports/ImportView";
import { OpportunityDetailView } from "./features/opportunities/OpportunityDetailView";
import { OpportunityDetailFitPanel } from "./features/opportunities/OpportunityFitBreakdown";
import { OpportunityList } from "./features/opportunities/OpportunityList";
import { ProfileSearchView } from "./features/profiles/ProfileSearchView";
import { PromptView } from "./features/prompts/PromptView";

type View =
  | "opportunities"
  | "profile"
  | "prompt"
  | "import"
  | "groups"
  | "duplicates"
  | "criteria";

const labels: Record<View, string> = {
  opportunities: "Opportunities",
  profile: "Profil & Suche",
  prompt: "Recherche",
  import: "Import",
  groups: "Groups & Waves",
  duplicates: "Dubletten",
  criteria: "Assessment-Kriterien",
};

export default function App() {
  const [view, setView] = useState<View>("opportunities");
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(
    null,
  );
  const [refreshToken, setRefreshToken] = useState(0);

  function navigate(next: View) {
    setView(next);
    setSelectedOpportunity(null);
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
        <nav>
          {(Object.keys(labels) as View[]).map((item) => (
            <button
              className={view === item ? "active" : ""}
              key={item}
              onClick={() => navigate(item)}
            >
              {labels[item]}
            </button>
          ))}
        </nav>
        <p className="local-note">Lokal · privat · nachvollziehbar</p>
      </aside>
      <main className="content">
        {view === "opportunities" &&
          (selectedOpportunity ? (
            <>
              <OpportunityDetailFitPanel opportunityId={selectedOpportunity} />
              <OpportunityDetailView
                opportunityId={selectedOpportunity}
                onBack={() => setSelectedOpportunity(null)}
              />
            </>
          ) : (
            <OpportunityList
              refreshToken={refreshToken}
              onSelect={setSelectedOpportunity}
            />
          ))}
        {view === "profile" && <ProfileSearchView />}
        {view === "duplicates" && <DuplicateCasesView />}
        {view === "import" && (
          <ImportView
            onImported={() => setRefreshToken((value) => value + 1)}
          />
        )}
        {view === "groups" && <GroupsView />}
        {view === "criteria" && <CriteriaView />}
        {view === "prompt" && (
          <PromptView
            onImported={() => setRefreshToken((value) => value + 1)}
          />
        )}
      </main>
    </div>
  );
}
