import { useState } from "react";

import { CandidateProfileForm } from "./CandidateProfileForm";
import { EvaluationPolicyPanel } from "./EvaluationPolicyPanel";
import { SearchProfilesPanel } from "./SearchProfilesPanel";

type Tab = "candidate" | "search" | "evaluation";

export function ProfileSearchView() {
  const [tab, setTab] = useState<Tab>("candidate");

  return (
    <section className="page-stack profile-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Persönlicher Kontext</p>
          <h1>Profile</h1>
          <p className="page-description">
            Pflege dein persönliches Qualifikationsprofil und mehrere
            Suchstrategien getrennt voneinander. Die Daten bleiben lokal; nur
            ausdrücklich ausgewählte Inhalte werden in externe Prompts
            übernommen.
          </p>
        </div>
      </header>

      <div className="profile-tabs" role="tablist" aria-label="Profile">
        <button
          className={tab === "candidate" ? "active" : ""}
          onClick={() => setTab("candidate")}
          role="tab"
          aria-selected={tab === "candidate"}
          type="button"
        >
          Persönliches Profil
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
          Fit & Bewertung
        </button>
      </div>

      <section className="profile-workspace">
        {tab === "candidate" && <CandidateProfileForm />}
        {tab === "search" && <SearchProfilesPanel />}
        {tab === "evaluation" && <EvaluationPolicyPanel />}
      </section>
    </section>
  );
}
