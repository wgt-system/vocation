import { FormEvent, useState } from "react";

import { api } from "../../api/client";
import { ErrorState, Loading } from "../../components/AsyncState";

export function PromptView() {
  const [profile, setProfile] = useState("");
  const [constraints, setConstraints] = useState("");
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [prompt, setPrompt] = useState("");
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generate(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setCopied(false);
    try {
      const result = await api.generatePrompt({
        search_profile: profile,
        constraints: constraints
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
        as_of_date: asOfDate,
      });
      setPrompt(result.prompt_text);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Prompt konnte nicht erzeugt werden.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function copyPrompt() {
    await navigator.clipboard.writeText(prompt);
    setCopied(true);
  }

  function savePrompt() {
    const url = URL.createObjectURL(
      new Blob([prompt], { type: "text/plain;charset=utf-8" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `vocation-initial-research-${asOfDate}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">External Research</p>
          <h1>Initial Research Prompt</h1>
        </div>
      </header>
      <form className="panel stack" onSubmit={generate}>
        <label>
          Suchprofil
          <textarea
            rows={5}
            value={profile}
            onChange={(event) => setProfile(event.target.value)}
            required
          />
        </label>
        <label>
          Constraints, eine pro Zeile
          <textarea
            rows={4}
            value={constraints}
            onChange={(event) => setConstraints(event.target.value)}
          />
        </label>
        <label>
          Stichtag
          <input
            type="date"
            value={asOfDate}
            onChange={(event) => setAsOfDate(event.target.value)}
            required
          />
        </label>
        <button className="primary" type="submit" disabled={loading}>
          Self-contained Prompt erzeugen
        </button>
        {loading && (
          <Loading label="Prompt wird mit aktiven Kriterien erzeugt …" />
        )}
        {error && <ErrorState message={error} />}
      </form>
      {prompt && (
        <div className="panel stack">
          <h2>Generierter Prompt</h2>
          <textarea
            aria-label="Generierter Prompt"
            className="prompt-output"
            rows={22}
            readOnly
            value={prompt}
          />
          <div className="actions">
            <button className="primary" onClick={copyPrompt}>
              In Zwischenablage kopieren
            </button>
            <button onClick={savePrompt}>Als Textdatei speichern</button>
            {copied && <span role="status">Kopiert.</span>}
          </div>
        </div>
      )}
    </section>
  );
}
