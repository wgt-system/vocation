import { useState } from "react";

import { CriteriaView } from "../criteria/CriteriaView";
import { DuplicateCasesView } from "../duplicates/DuplicateCasesView";
import { ImportView } from "../imports/ImportView";

type ToolsTab = "import" | "criteria" | "duplicates";

export function ToolsView({ onImported }: { onImported: () => void }) {
  const [tab, setTab] = useState<ToolsTab>("import");

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Erweiterte Funktionen</p>
          <h1>Werkzeuge</h1>
          <p className="page-description">
            Manueller JSON-Import, Kriterienverwaltung und technische
            Dublettenprüfung bleiben erreichbar, ohne den normalen Arbeitsablauf
            zu überladen.
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
          Bewertungskriterien
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "duplicates"}
          className={tab === "duplicates" ? "active" : ""}
          onClick={() => setTab("duplicates")}
        >
          Dubletten prüfen
        </button>
      </div>
      {tab === "import" && <ImportView onImported={onImported} />}
      {tab === "criteria" && <CriteriaView />}
      {tab === "duplicates" && <DuplicateCasesView />}
    </section>
  );
}
