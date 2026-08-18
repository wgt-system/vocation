import { useState } from "react";

import { CriteriaView } from "../criteria/CriteriaView";
import { ImportView } from "../imports/ImportView";

type ToolsTab = "import" | "criteria";

export function ToolsView({ onImported }: { onImported: () => void }) {
  const [tab, setTab] = useState<ToolsTab>("import");

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Erweiterte Funktionen</p>
          <h1>Werkzeuge</h1>
          <p>
            Manueller JSON-Import und direkte Kriterienverwaltung bleiben verfügbar,
            gehören aber nicht zum normalen Recherche-Workflow.
          </p>
        </div>
      </header>
      <div className="profile-tabs" role="tablist" aria-label="Werkzeuge">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "import"}
          className={tab === "import" ? "active" : ""}
          onClick={() => setTab("import")}
        >
          Manueller Import
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "criteria"}
          className={tab === "criteria" ? "active" : ""}
          onClick={() => setTab("criteria")}
        >
          Assessment-Kriterien
        </button>
      </div>
      {tab === "import" ? <ImportView onImported={onImported} /> : <CriteriaView />}
    </section>
  );
}
