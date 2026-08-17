import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { api, type DuplicateCaseReview } from "../api/client";
import { DuplicateCasesView } from "./duplicates/DuplicateCasesView";

const opportunityCase: DuplicateCaseReview = {
  id: "case-opportunity",
  subject_type: "opportunity",
  left_subject: {
    subject_type: "opportunity",
    subject_id: "opp-left",
    title: "Junior Developer",
    context: "Example GmbH",
  },
  right_subject: {
    subject_type: "opportunity",
    subject_id: "opp-right",
    title: "Junior Software Developer",
    context: "Example GmbH",
  },
  evidence_summary: "Titel und Arbeitgeber überschneiden sich.",
  confidence: 0.8,
  source_references: [
    {
      source_reference_id: "ref-1",
      source_name: "Example Jobs",
      display_label: "Originalanzeige",
      url: "https://example.test/jobs/one",
      observed_at: "2026-08-17T00:00:00Z",
    },
  ],
  created_at: "2026-08-17T00:00:00Z",
  current_decision: null,
  decision_history: [],
  is_reviewed: false,
  is_resolved: false,
};

const postingCase: DuplicateCaseReview = {
  id: "case-posting",
  subject_type: "posting",
  left_subject: {
    subject_type: "posting",
    subject_id: "posting-left",
    title: "Developer Posting",
    context: "Example Jobs",
  },
  right_subject: {
    subject_type: "posting",
    subject_id: "posting-right",
    title: "Developer Posting Mirror",
    context: "Company Careers",
  },
  evidence_summary: "Beide Anzeigen beschreiben möglicherweise dieselbe Stelle.",
  confidence: 0.6,
  source_references: [],
  created_at: "2026-08-17T01:00:00Z",
  current_decision: {
    id: "decision-1",
    duplicate_case_id: "case-posting",
    sequence: 1,
    outcome: "confirmed_distinct",
    reason: "Unterschiedliche externe Posting-IDs.",
    decided_at: "2026-08-17T02:00:00Z",
  },
  decision_history: [
    {
      id: "decision-1",
      duplicate_case_id: "case-posting",
      sequence: 1,
      outcome: "confirmed_distinct",
      reason: "Unterschiedliche externe Posting-IDs.",
      decided_at: "2026-08-17T02:00:00Z",
    },
  ],
  is_reviewed: true,
  is_resolved: true,
};

afterEach(() => {
  vi.restoreAllMocks();
});

describe("DuplicateCasesView", () => {
  it("shows unresolved cases by default and filters resolved cases without making evidence URLs clickable", async () => {
    vi.spyOn(api, "listDuplicateCases").mockResolvedValue([
      opportunityCase,
      postingCase,
    ]);
    const user = userEvent.setup();

    render(<DuplicateCasesView />);

    expect(await screen.findByText("Junior Developer")).toBeInTheDocument();
    expect(
      screen.queryByText("Developer Posting Mirror"),
    ).not.toBeInTheDocument();
    const evidenceUrl = screen.getByText("https://example.test/jobs/one");
    expect(evidenceUrl.closest("a")).toBeNull();

    await user.selectOptions(screen.getByLabelText("Dubletten filtern"), "resolved");
    expect(await screen.findByText("Developer Posting Mirror")).toBeInTheDocument();
    expect(screen.queryByText("Junior Developer")).not.toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Dubletten filtern"), "all");
    expect(screen.getByText("Junior Developer")).toBeInTheDocument();
    expect(screen.getByText("Developer Posting Mirror")).toBeInTheDocument();
  });

  it("submits an explicit decision with a required reason and updates the review state", async () => {
    vi.spyOn(api, "listDuplicateCases").mockResolvedValue([opportunityCase]);
    const decided: DuplicateCaseReview = {
      ...opportunityCase,
      current_decision: {
        id: "decision-new",
        duplicate_case_id: opportunityCase.id,
        sequence: 1,
        outcome: "confirmed_duplicate",
        reason: "Dieselbe zugrunde liegende Stelle.",
        decided_at: "2026-08-17T03:00:00Z",
      },
      decision_history: [
        {
          id: "decision-new",
          duplicate_case_id: opportunityCase.id,
          sequence: 1,
          outcome: "confirmed_duplicate",
          reason: "Dieselbe zugrunde liegende Stelle.",
          decided_at: "2026-08-17T03:00:00Z",
        },
      ],
      is_reviewed: true,
      is_resolved: true,
    };
    const decide = vi.spyOn(api, "decideDuplicateCase").mockResolvedValue(decided);
    const user = userEvent.setup();

    render(<DuplicateCasesView />);
    await screen.findByText("Junior Developer");

    await user.click(screen.getByRole("button", { name: "Entscheidung speichern" }));
    expect(
      screen.getByText("Bitte einen Entscheidungsgrund eingeben."),
    ).toBeInTheDocument();
    expect(decide).not.toHaveBeenCalled();

    await user.type(
      screen.getByLabelText(`Entscheidungsgrund für ${opportunityCase.id}`),
      "Dieselbe zugrunde liegende Stelle.",
    );
    await user.click(screen.getByRole("button", { name: "Entscheidung speichern" }));

    await waitFor(() =>
      expect(decide).toHaveBeenCalledWith(opportunityCase.id, {
        outcome: "confirmed_duplicate",
        reason: "Dieselbe zugrunde liegende Stelle.",
      }),
    );
    expect(
      await screen.findByText("Entschieden · Identisch"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Dieselbe zugrunde liegende Stelle\./),
    ).toBeInTheDocument();
  });

  it("offers classification only and never exposes merge or delete controls", async () => {
    vi.spyOn(api, "listDuplicateCases").mockResolvedValue([opportunityCase]);

    render(<DuplicateCasesView />);
    await screen.findByText("Junior Developer");

    expect(screen.getByRole("option", { name: "Identisch" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Getrennt" })).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Verwandt, aber getrennt" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Ungeklärt lassen" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /merge/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /löschen/i })).not.toBeInTheDocument();
  });
});
