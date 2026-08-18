import { useEffect, useMemo, useState } from "react";

import {
  searchVocabularyApi,
  type ReviewedSearchVocabularyBundle,
  type SearchVocabularyEntry,
  type SearchVocabularyKind,
  type SearchVocabularyProposalBundle,
} from "./searchVocabularyApi";

const kindLabels: Record<SearchVocabularyKind, string> = {
  role: "Rollen",
  technology: "Technologien",
  industry: "Branchen",
  seniority: "Seniorität",
  employment_type: "Beschäftigungsarten",
};

const refreshableKinds = ["role", "technology", "industry"] as const;

function localIsoDate() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

export function SearchVocabularyManager() {
  const [kind, setKind] = useState<SearchVocabularyKind>("role");
  const [query, setQuery] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [entries, setEntries] = useState<SearchVocabularyEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [customLabel, setCustomLabel] = useState("");
  const [customAliases, setCustomAliases] = useState("");
  const [customGroup, setCustomGroup] = useState("");
  const [savingCustom, setSavingCustom] = useState(false);

  const [asOfDate, setAsOfDate] = useState(localIsoDate());
  const [refreshKinds, setRefreshKinds] = useState<
    (typeof refreshableKinds)[number][]
  >([...refreshableKinds]);
  const [generatedPrompt, setGeneratedPrompt] = useState("");
  const [proposalJson, setProposalJson] = useState("");
  const [reviewed, setReviewed] =
    useState<ReviewedSearchVocabularyBundle | null>(null);
  const [reviewError, setReviewError] = useState("");
  const [acceptedLabels, setAcceptedLabels] = useState<Set<string>>(new Set());

  const activeCount = useMemo(
    () => entries.filter((entry) => entry.is_active).length,
    [entries],
  );

  async function loadEntries() {
    setLoading(true);
    setError("");
    try {
      setEntries(
        await searchVocabularyApi.list({
          kind,
          query,
          includeInactive,
        }),
      );
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Katalog konnte nicht geladen werden.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timeout = window.setTimeout(() => void loadEntries(), 150);
    return () => window.clearTimeout(timeout);
  }, [kind, query, includeInactive]);

  async function createCustom() {
    if (!customLabel.trim()) return;
    setSavingCustom(true);
    setError("");
    try {
      await searchVocabularyApi.createCustom({
        kind,
        label: customLabel.trim(),
        aliases: customAliases
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
        group: customGroup.trim() || null,
      });
      setCustomLabel("");
      setCustomAliases("");
      setCustomGroup("");
      await loadEntries();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Begriff konnte nicht angelegt werden.",
      );
    } finally {
      setSavingCustom(false);
    }
  }

  async function toggleEntry(entry: SearchVocabularyEntry) {
    setError("");
    try {
      await searchVocabularyApi.update(entry.id, {
        is_active: !entry.is_active,
      });
      await loadEntries();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Begriff konnte nicht aktualisiert werden.",
      );
    }
  }

  function toggleRefreshKind(value: (typeof refreshableKinds)[number]) {
    setRefreshKinds((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    );
  }

  async function generateRefreshPrompt() {
    setReviewError("");
    try {
      const generated = await searchVocabularyApi.generateRefreshPrompt({
        as_of_date: asOfDate,
        kinds: refreshKinds,
      });
      setGeneratedPrompt(generated.prompt_text);
    } catch (reason) {
      setReviewError(
        reason instanceof Error
          ? reason.message
          : "Aktualisierungsprompt konnte nicht erzeugt werden.",
      );
    }
  }

  async function reviewProposals() {
    setReviewError("");
    setReviewed(null);
    setAcceptedLabels(new Set());
    try {
      const parsed = JSON.parse(proposalJson) as SearchVocabularyProposalBundle;
      setReviewed(await searchVocabularyApi.reviewProposals(parsed));
    } catch (reason) {
      setReviewError(
        reason instanceof Error
          ? reason.message
          : "Vorschläge konnten nicht geprüft werden.",
      );
    }
  }

  async function acceptProposal(
    proposal: ReviewedSearchVocabularyBundle["proposals"][number]["proposal"],
  ) {
    setReviewError("");
    try {
      await searchVocabularyApi.createCustom({
        kind: proposal.kind,
        label: proposal.label,
        aliases: proposal.aliases,
        group: proposal.group,
      });
      setAcceptedLabels((current) => new Set(current).add(proposal.label));
      if (proposal.kind === kind) await loadEntries();
    } catch (reason) {
      setReviewError(
        reason instanceof Error
          ? reason.message
          : "Vorschlag konnte nicht übernommen werden.",
      );
    }
  }

  return (
    <div className="stack vocabulary-manager">
      <section className="panel stack">
        <div className="section-heading">
          <h2>Suchkataloge</h2>
          <p>
            Stabile Begriffe für Suchprofile. Eigene Begriffe bleiben möglich;
            deaktivierte Begriffe bleiben für historische Profile erhalten.
          </p>
        </div>

        <div className="vocabulary-toolbar">
          <label>
            <span>Katalog</span>
            <select
              aria-label="Suchkatalog auswählen"
              value={kind}
              onChange={(event) =>
                setKind(event.target.value as SearchVocabularyKind)
              }
            >
              {Object.entries(kindLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="search-field">
            <span>Begriffe durchsuchen</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Name oder Alias"
            />
          </label>
          <label className="checkbox-label vocabulary-inactive-toggle">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(event) => setIncludeInactive(event.target.checked)}
            />
            Deaktivierte anzeigen
          </label>
        </div>

        <p className="muted">
          {loading
            ? "Katalog wird geladen …"
            : `${activeCount} aktive Einträge in dieser Ansicht`}
        </p>
        {error && (
          <p className="state state-error" role="alert">
            {error}
          </p>
        )}

        {!loading && (
          <div className="vocabulary-list">
            {entries.map((entry) => (
              <article
                className={`vocabulary-entry ${entry.is_active ? "" : "inactive"}`}
                key={entry.id}
              >
                <div>
                  <strong>{entry.label}</strong>
                  <div className="vocabulary-meta">
                    {entry.group && <span>{entry.group}</span>}
                    {entry.is_custom && <span>Eigener Begriff</span>}
                    {!entry.is_active && <span>Deaktiviert</span>}
                  </div>
                  {entry.aliases.length > 0 && (
                    <small>Aliasse: {entry.aliases.join(" · ")}</small>
                  )}
                </div>
                <button type="button" onClick={() => void toggleEntry(entry)}>
                  {entry.is_active ? "Deaktivieren" : "Reaktivieren"}
                </button>
              </article>
            ))}
            {entries.length === 0 && (
              <p className="muted">Keine passenden Begriffe.</p>
            )}
          </div>
        )}
      </section>

      <section className="panel stack">
        <div className="section-heading">
          <h2>Eigenen Begriff anlegen</h2>
          <p>
            Für neue oder sehr spezielle Rollen, Technologien und Branchen muss
            nicht auf ein Software-Update gewartet werden.
          </p>
        </div>
        <div className="vocabulary-custom-grid">
          <label>
            <span>Name</span>
            <input
              value={customLabel}
              onChange={(event) => setCustomLabel(event.target.value)}
            />
          </label>
          <label>
            <span>Gruppe (optional)</span>
            <input
              value={customGroup}
              onChange={(event) => setCustomGroup(event.target.value)}
            />
          </label>
          <label className="vocabulary-alias-field">
            <span>Aliasse (optional, durch Komma getrennt)</span>
            <input
              value={customAliases}
              onChange={(event) => setCustomAliases(event.target.value)}
              placeholder="Alternative Bezeichnung, weitere Schreibweise"
            />
          </label>
        </div>
        <div className="actions">
          <button
            type="button"
            className="primary"
            disabled={!customLabel.trim() || savingCustom}
            onClick={() => void createCustom()}
          >
            {savingCustom ? "Wird gespeichert …" : "Begriff hinzufügen"}
          </button>
        </div>
      </section>

      <section className="panel stack">
        <div className="section-heading">
          <h2>Katalog aktualisieren</h2>
          <p>
            Erzeuge einen Rechercheprompt für neue Marktbegriffe. Externe
            Vorschläge ändern den Katalog niemals automatisch: erst prüfen,
            danach einzelne Vorschläge übernehmen.
          </p>
        </div>

        <div className="vocabulary-refresh-controls">
          <label>
            <span>Stand</span>
            <input
              type="date"
              value={asOfDate}
              onChange={(event) => setAsOfDate(event.target.value)}
            />
          </label>
          <fieldset>
            <legend>Rechercheumfang</legend>
            <div className="filter-chip-row">
              {refreshableKinds.map((value) => (
                <label
                  className={`filter-chip ${refreshKinds.includes(value) ? "active" : ""}`}
                  key={value}
                >
                  <input
                    type="checkbox"
                    checked={refreshKinds.includes(value)}
                    onChange={() => toggleRefreshKind(value)}
                  />
                  {kindLabels[value]}
                </label>
              ))}
            </div>
          </fieldset>
          <button
            type="button"
            className="primary"
            disabled={refreshKinds.length === 0}
            onClick={() => void generateRefreshPrompt()}
          >
            Aktualisierungsprompt erzeugen
          </button>
        </div>

        {generatedPrompt && (
          <div className="stack">
            <label>
              <span>Rechercheprompt</span>
              <textarea
                className="prompt-textarea"
                readOnly
                value={generatedPrompt}
              />
            </label>
            <div className="actions">
              <button
                type="button"
                onClick={() =>
                  void navigator.clipboard.writeText(generatedPrompt)
                }
              >
                Prompt kopieren
              </button>
            </div>
          </div>
        )}

        <label>
          <span>Zurückgegebenes Vorschlags-JSON</span>
          <textarea
            aria-label="Katalogvorschläge JSON"
            className="prompt-result-input"
            value={proposalJson}
            onChange={(event) => setProposalJson(event.target.value)}
            placeholder='{"contract":"vocation.search-vocabulary-proposals","version":"1.0",...}'
          />
        </label>
        <div className="actions">
          <button
            type="button"
            disabled={!proposalJson.trim()}
            onClick={() => void reviewProposals()}
          >
            Vorschläge prüfen
          </button>
        </div>
        {reviewError && (
          <p className="state state-error" role="alert">
            {reviewError}
          </p>
        )}

        {reviewed && (
          <div className="vocabulary-proposals">
            {reviewed.proposals.length === 0 && (
              <p className="muted">Keine neuen Vorschläge.</p>
            )}
            {reviewed.proposals.map(
              ({ proposal, already_known_entry_id: knownId }) => {
                const accepted = acceptedLabels.has(proposal.label);
                return (
                  <article
                    className="vocabulary-proposal"
                    key={`${proposal.kind}:${proposal.label}`}
                  >
                    <div>
                      <span className="eyebrow">
                        {kindLabels[proposal.kind]}
                      </span>
                      <strong>{proposal.label}</strong>
                      <p>{proposal.reason}</p>
                      {proposal.aliases.length > 0 && (
                        <small>Aliasse: {proposal.aliases.join(" · ")}</small>
                      )}
                      <div className="vocabulary-sources">
                        {proposal.source_urls.map((url) => (
                          <a
                            key={url}
                            href={url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Quelle öffnen
                          </a>
                        ))}
                      </div>
                    </div>
                    {knownId ? (
                      <span className="status-badge">Bereits vorhanden</span>
                    ) : accepted ? (
                      <span className="status-badge">Übernommen</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => void acceptProposal(proposal)}
                      >
                        Übernehmen
                      </button>
                    )}
                  </article>
                );
              },
            )}
          </div>
        )}
      </section>
    </div>
  );
}
