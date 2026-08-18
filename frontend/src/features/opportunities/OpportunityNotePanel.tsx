import { useEffect, useState } from "react";

import { Loading } from "../../components/AsyncState";
import { opportunityNoteApi, type OpportunityNote } from "./opportunityNoteApi";

function errorMessage(reason: unknown): string {
  return reason instanceof Error
    ? reason.message
    : "Persönliche Notiz konnte nicht gespeichert werden.";
}

export function OpportunityNotePanel({
  opportunityId,
}: {
  opportunityId: string;
}) {
  const [note, setNote] = useState<OpportunityNote | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setMessage("");
    opportunityNoteApi
      .get(opportunityId)
      .then((next) => {
        if (!active) return;
        setNote(next);
        setContent(next?.content ?? "");
      })
      .catch((reason) => {
        if (!active) return;
        setError(errorMessage(reason));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [opportunityId]);

  async function save() {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const next = await opportunityNoteApi.save(opportunityId, content);
      setNote(next);
      setContent(next?.content ?? "");
      setMessage(
        next ? "Persönliche Notiz gespeichert." : "Persönliche Notiz gelöscht.",
      );
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel opportunity-note-panel">
      <div>
        <p className="eyebrow">Privater Vocation-Zustand</p>
        <h2>Persönliche Notiz</h2>
        <p className="muted">
          Wird nicht in Research Bundles übernommen und beeinflusst den Fit
          nicht automatisch.
        </p>
      </div>
      {loading ? (
        <Loading label="Persönliche Notiz wird geladen …" />
      ) : (
        <>
          <label>
            Notiz
            <textarea
              aria-label="Persönliche Opportunity-Notiz"
              maxLength={50_000}
              rows={6}
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="Eigene Gedanken, Rückfragen oder nächste Schritte …"
            />
          </label>
          <div className="actions">
            <button
              className="primary"
              type="button"
              disabled={saving}
              onClick={() => void save()}
            >
              {saving ? "Speichert …" : "Notiz speichern"}
            </button>
            {note && (
              <small>
                Zuletzt gespeichert:{" "}
                {new Date(note.updated_at).toLocaleString("de-DE")}
              </small>
            )}
          </div>
        </>
      )}
      {message && <p role="status">{message}</p>}
      {error && (
        <p className="state state-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
