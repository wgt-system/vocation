import { useState } from "react";

import { CandidateProfileForm } from "./CandidateProfileForm";
import { EvaluationPolicyPanel } from "./EvaluationPolicyPanel";
import { SearchProfilesPanel } from "./SearchProfilesPanel";

type Tab = "candidate" | "search" | "evaluation";

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
            Suchstrategien als Grundlage für Recherche und erklärbare
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
        <button
          className={tab === "evaluation" ? "active" : ""}
          onClick={() => setTab("evaluation")}
          role="tab"
          aria-selected={tab === "evaluation"}
          type="button"
        >
          Bewertung
        </button>
      </div>

      <section className="panel profile-workspace">
        {tab === "candidate" && <CandidateProfileForm />}
        {tab === "search" && <SearchProfilesPanel />}
        {tab === "evaluation" && <EvaluationPolicyPanel />}
      </section>
    </section>
  );
}
