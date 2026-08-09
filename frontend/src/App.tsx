import { useState } from "react";

import { CriteriaView } from "./features/criteria/CriteriaView";
import { ImportView } from "./features/imports/ImportView";
import { OpportunityDetailView } from "./features/opportunities/OpportunityDetailView";
import { OpportunityList } from "./features/opportunities/OpportunityList";
import { PromptView } from "./features/prompts/PromptView";

type View = "opportunities" | "import" | "criteria" | "prompt";

const labels: Record<View, string> = {
  opportunities: "Opportunities",
  import: "Import",
  criteria: "Assessment-Kriterien",
  prompt: "Research Prompt",
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
            <small>Local job market</small>
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
        <p className="local-note">Lokal · eigenständig · keine LLM-API</p>
      </aside>
      <main className="content">
        {view === "opportunities" &&
          (selectedOpportunity ? (
            <OpportunityDetailView
              opportunityId={selectedOpportunity}
              onBack={() => setSelectedOpportunity(null)}
            />
          ) : (
            <OpportunityList
              refreshToken={refreshToken}
              onSelect={setSelectedOpportunity}
            />
          ))}
        {view === "import" && (
          <ImportView
            onImported={() => setRefreshToken((value) => value + 1)}
          />
        )}
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
