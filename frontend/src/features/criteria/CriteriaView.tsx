import { FormEvent, useEffect, useState } from "react";

import { api, type Criterion } from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

const blank: Omit<Criterion, "revision"> = {
  criterion_id: "",
  display_name: "",
  description: "",
  value_type: "numeric",
  numeric_min: 1,
  numeric_max: 5,
  allowed_values: [],
  applicable_subject_type: "opportunity",
  active: true,
  display_order: 10,
};

export function CriteriaView() {
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [form, setForm] = useState<Omit<Criterion, "revision">>(blank);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function reload() {
    setLoading(true);
    try {
      setCriteria(await api.listCriteria());
      setError("");
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Kriterien konnten nicht geladen werden.",
      );
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void reload();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    const normalized = {
      ...form,
      numeric_min: form.value_type === "numeric" ? form.numeric_min : null,
      numeric_max: form.value_type === "numeric" ? form.numeric_max : null,
      allowed_values:
        form.value_type === "categorical" ? form.allowed_values : [],
    };
    try {
      if (editing) await api.editCriterion(normalized);
      else
        await api.createCriterion({
          ...normalized,
          display_order: criteria.length * 10 + 10,
        });
      setForm(blank);
      setEditing(false);
      await reload();
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Kriterium konnte nicht gespeichert werden.",
      );
    }
  }

  async function move(index: number, direction: number) {
    const target = index + direction;
    if (target < 0 || target >= criteria.length) return;
    const next = [...criteria];
    [next[index], next[target]] = [next[target], next[index]];
    try {
      setCriteria(
        await api.reorderCriteria(next.map((item) => item.criterion_id)),
      );
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Reihenfolge konnte nicht gespeichert werden.",
      );
    }
  }

  function beginEdit(item: Criterion) {
    const { revision: _revision, ...payload } = item;
    setForm(payload);
    setEditing(true);
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Vocation-owned</p>
          <h1>Assessment-Kriterien</h1>
        </div>
      </header>
      {loading && <Loading />}
      {error && <ErrorState message={error} />}
      {!loading && criteria.length === 0 && (
        <EmptyState>Noch keine Kriterien angelegt.</EmptyState>
      )}
      <div className="criterion-list">
        {criteria.map((item, index) => (
          <article
            className={`criterion ${item.active ? "" : "muted"}`}
            key={item.criterion_id}
          >
            <div>
              <p className="eyebrow">
                {item.criterion_id} · Revision {item.revision}
              </p>
              <h2>{item.display_name}</h2>
              <p>{item.description}</p>
              <small>
                {item.value_type} · {item.applicable_subject_type}
                {item.numeric_min !== null
                  ? ` · ${item.numeric_min}–${item.numeric_max}`
                  : ""}
                {item.allowed_values?.length
                  ? ` · ${item.allowed_values.join(", ")}`
                  : ""}
              </small>
            </div>
            <div className="actions">
              <button
                aria-label={`${item.display_name} nach oben`}
                onClick={() => move(index, -1)}
              >
                ↑
              </button>
              <button
                aria-label={`${item.display_name} nach unten`}
                onClick={() => move(index, 1)}
              >
                ↓
              </button>
              <button onClick={() => beginEdit(item)}>Bearbeiten</button>
              <button
                onClick={async () => {
                  await api.activateCriterion(item.criterion_id, !item.active);
                  await reload();
                }}
              >
                {item.active ? "Deaktivieren" : "Aktivieren"}
              </button>
            </div>
          </article>
        ))}
      </div>
      <form className="panel form-grid" onSubmit={save}>
        <h2>{editing ? "Kriterium bearbeiten" : "Neues Kriterium"}</h2>
        <label>
          Criterion ID
          <input
            value={form.criterion_id}
            disabled={editing}
            onChange={(event) =>
              setForm({ ...form, criterion_id: event.target.value })
            }
            required
          />
        </label>
        <label>
          Anzeigename
          <input
            value={form.display_name}
            onChange={(event) =>
              setForm({ ...form, display_name: event.target.value })
            }
            required
          />
        </label>
        <label className="full">
          Beschreibung
          <textarea
            value={form.description}
            onChange={(event) =>
              setForm({ ...form, description: event.target.value })
            }
          />
        </label>
        <label>
          Werttyp
          <select
            value={form.value_type}
            onChange={(event) =>
              setForm({
                ...form,
                value_type: event.target.value as Criterion["value_type"],
              })
            }
          >
            <option value="numeric">Numerisch</option>
            <option value="boolean">Ja/Nein</option>
            <option value="categorical">Kategorie</option>
            <option value="text">Freitext</option>
          </select>
        </label>
        <label>
          Subject
          <select
            value={form.applicable_subject_type}
            onChange={(event) =>
              setForm({
                ...form,
                applicable_subject_type: event.target
                  .value as Criterion["applicable_subject_type"],
              })
            }
          >
            <option value="opportunity">Opportunity</option>
            <option value="company">Company</option>
            <option value="posting">Posting</option>
          </select>
        </label>
        {form.value_type === "numeric" && (
          <>
            <label>
              Minimum
              <input
                type="number"
                value={form.numeric_min ?? 1}
                onChange={(event) =>
                  setForm({ ...form, numeric_min: Number(event.target.value) })
                }
              />
            </label>
            <label>
              Maximum
              <input
                type="number"
                value={form.numeric_max ?? 5}
                onChange={(event) =>
                  setForm({ ...form, numeric_max: Number(event.target.value) })
                }
              />
            </label>
          </>
        )}
        {form.value_type === "categorical" && (
          <label className="full">
            Erlaubte Werte, kommasepariert
            <input
              value={form.allowed_values?.join(", ") ?? ""}
              onChange={(event) =>
                setForm({
                  ...form,
                  allowed_values: event.target.value
                    .split(",")
                    .map((value) => value.trim())
                    .filter(Boolean),
                })
              }
            />
          </label>
        )}
        <div className="actions full">
          <button className="primary" type="submit">
            Speichern
          </button>
          {editing && (
            <button
              type="button"
              onClick={() => {
                setEditing(false);
                setForm(blank);
              }}
            >
              Abbrechen
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
