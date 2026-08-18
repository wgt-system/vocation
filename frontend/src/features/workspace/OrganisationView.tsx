import { useState } from "react";

import { DuplicateCasesView } from "../duplicates/DuplicateCasesView";
import { GroupsView } from "../groups/GroupsView";

type OrganisationTab = "groups" | "duplicates";

export function OrganisationView() {
  const [tab, setTab] = useState<OrganisationTab>("groups");

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Markt organisieren</p>
          <h1>Organisation</h1>
          <p>Arbeite mit Groups/Waves und kläre mögliche Dubletten an einem Ort.</p>
        </div>
      </header>
      <div className="profile-tabs" role="tablist" aria-label="Organisation">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "groups"}
          className={tab === "groups" ? "active" : ""}
          onClick={() => setTab("groups")}
        >
          Groups & Waves
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
      {tab === "groups" ? <GroupsView /> : <DuplicateCasesView />}
    </section>
  );
}
