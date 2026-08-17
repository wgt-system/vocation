import { useState } from "react";

import { CandidateProfileForm } from "./CandidateProfileForm";
import { SearchProfilesPanel } from "./SearchProfilesPanel";

type Tab = "candidate" | "search";

export function ProfileSearchView() {
  const [tab, setTab] = useState<Tab>("candidate");

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Persönlicher Kontext für qualitative Jobsuche
          </p>
          <h1>Profil &amp; Suche</h1>
          <p className="muted">
            Vocation nutzt dein privates Qualifikationsprofil und deine
            Suchstrategien als Grundlage für Recherche, Bewertung und spätere
            Fit-Analyse. Diese Daten bleiben lokal und werden nicht publiziert.
          </p>
        </div>
      </header>

      <div className="profile-tabs" role="tablist" aria-label="Profil & Suche">
        <button
          className={tab === "candidate" ? "active" : ""}
          onClick={() => setTab("candidate")}
          role="tab"
          aria-selected={tab === "candidate"}
          type="button"
        >
          Mein Profil
        </button>
        <button
          className={tab === "search" ? "active" : ""}
          onClick={() => setTab("search")}
          role="tab"
          aria-selected={tab === "search"}
          type="button"
        >
          Suchprofile
        </button>
      </div>

      <section className="panel profile-workspace">
        {tab === "candidate" ? (
          <CandidateProfileForm />
        ) : (
          <SearchProfilesPanel />
        )}
      </section>
    </section>
  );
}
