import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { type CandidateProfile, profileApi, type SearchProfile } from "./profileApi";
import { ProfileSearchView } from "./ProfileSearchView";

vi.mock("./profileApi", async () => {
  const actual = await vi.importActual<typeof import("./profileApi")>("./profileApi");
  return {
    ...actual,
    profileApi: {
      getCandidate: vi.fn(),
      saveCandidate: vi.fn(),
      listSearchProfiles: vi.fn(),
      createSearchProfile: vi.fn(),
      reviseSearchProfile: vi.fn(),
      setDefaultSearchProfile: vi.fn(),
      deleteSearchProfile: vi.fn(),
    },
  };
});

const candidate: CandidateProfile = {
  revision: 2,
  headline: "Junior Softwareentwickler",
  summary: "Informatikprofil mit Softwareentwicklungsfokus.",
  education: [
    {
      degree: "B.Sc.",
      field: "Informatik",
      institution: "Beispieluniversität",
      status: "completed",
      graduation_year: 2026,
    },
  ],
  skills: [{ name: "Java", level: "strong", notes: "Backend" }],
  languages: [{ name: "Deutsch", level: "native" }],
  experience_summary: "Studium und Projekte",
  projects: [
    { name: "Projekt", summary: "Lokale App", technologies: ["Java"] },
  ],
  interests: ["Open Source"],
};

const searchProfile: SearchProfile = {
  id: "search-1",
  revision: 3,
  is_default: true,
  name: "Junior Hamburg",
  description: "Qualitative Einstiegsstellen",
  target_roles: ["Junior Softwareentwickler"],
  seniority_targets: ["Junior"],
  preferred_technologies: ["Java"],
  acceptable_technologies: ["C++"],
  avoided_technologies: [],
  target_locations: ["Hamburg"],
  work_models: ["hybrid"],
  relocation_willing: false,
  employment_types: ["full-time"],
  preferred_industries: [],
  avoided_industries: [],
  preferred_company_characteristics: ["Gute Einarbeitung"],
  avoided_company_characteristics: [],
  salary_floor: 40000,
  salary_target: 50000,
  salary_currency: "EUR",
  must_haves: ["Berufseinstieg möglich"],
  must_not_haves: ["Mehrjährige Berufserfahrung zwingend"],
  result_limit: 10,
};

describe("Profil & Suche", () => {
  beforeEach(() => {
    vi.mocked(profileApi.getCandidate).mockResolvedValue(candidate);
    vi.mocked(profileApi.saveCandidate).mockResolvedValue({
      ...candidate,
      revision: 3,
      headline: "Softwareentwickler",
    });
    vi.mocked(profileApi.listSearchProfiles).mockResolvedValue([searchProfile]);
    vi.mocked(profileApi.reviseSearchProfile).mockResolvedValue({
      ...searchProfile,
      revision: 4,
    });
    vi.mocked(profileApi.createSearchProfile).mockResolvedValue(searchProfile);
    vi.mocked(profileApi.setDefaultSearchProfile).mockResolvedValue(searchProfile);
    vi.mocked(profileApi.deleteSearchProfile).mockResolvedValue(undefined);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("loads and revises the private candidate profile without JSON editing", async () => {
    const user = userEvent.setup();
    render(<ProfileSearchView />);

    expect(await screen.findByDisplayValue("Junior Softwareentwickler")).toBeInTheDocument();
    expect(screen.getByDisplayValue("B.Sc.")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Java")).toBeInTheDocument();
    expect(screen.getByText(/Aktuelle Revision: 2/)).toBeInTheDocument();

    const headline = screen.getByLabelText("Profilüberschrift");
    await user.clear(headline);
    await user.type(headline, "Softwareentwickler");
    await user.click(screen.getByRole("button", { name: "Neue Revision speichern" }));

    expect(profileApi.saveCandidate).toHaveBeenCalledWith(
      expect.objectContaining({
        headline: "Softwareentwickler",
        education: [expect.objectContaining({ field: "Informatik" })],
        skills: [expect.objectContaining({ name: "Java", level: "strong" })],
      }),
    );
    expect(await screen.findByText("Profil gespeichert.")).toBeInTheDocument();
  });

  it("shows persisted search strategies and their hard quality constraints", async () => {
    const user = userEvent.setup();
    render(<ProfileSearchView />);

    await user.click(screen.getByRole("tab", { name: "Suchprofile" }));

    expect(await screen.findByRole("button", { name: /Junior Hamburg/ })).toBeInTheDocument();
    expect(screen.getByText(/aktives Standardprofil/)).toBeInTheDocument();
    expect(screen.getByDisplayValue("Junior Softwareentwickler")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Hamburg")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Berufseinstieg möglich")).toBeInTheDocument();
    expect(
      screen.getByDisplayValue("Mehrjährige Berufserfahrung zwingend"),
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue("10")).toBeInTheDocument();
  });

  it("creates a new quality-first search profile from normal form fields", async () => {
    const user = userEvent.setup();
    render(<ProfileSearchView />);
    await user.click(screen.getByRole("tab", { name: "Suchprofile" }));
    await screen.findByRole("button", { name: /Junior Hamburg/ });
    await user.click(screen.getByRole("button", { name: "+ Neu" }));

    await user.type(screen.getByLabelText("Name"), "C++ Hamburg");
    await user.type(screen.getByLabelText("Ziel & Schwerpunkt"), "Wenige hochwertige C++-Einstiegsrollen");
    await user.type(screen.getByLabelText("Zielrollen"), "Junior C++ Developer");
    await user.type(screen.getByLabelText("Bevorzugte Technologien"), "C++");
    await user.type(screen.getByLabelText("Zielorte"), "Hamburg");
    await user.type(screen.getByLabelText("Muss erfüllt sein"), "Junior geeignet");
    await user.type(screen.getByLabelText("Ausschlusskriterien"), "Senior-only");

    const resultLimit = screen.getByLabelText("Zielanzahl Ergebnisse");
    await user.clear(resultLimit);
    await user.type(resultLimit, "8");
    await user.click(screen.getByRole("button", { name: "Suchprofil anlegen" }));

    expect(profileApi.createSearchProfile).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "C++ Hamburg",
        target_roles: ["Junior C++ Developer"],
        preferred_technologies: ["C++"],
        target_locations: ["Hamburg"],
        must_haves: ["Junior geeignet"],
        must_not_haves: ["Senior-only"],
        result_limit: 8,
      }),
    );
  });
});
