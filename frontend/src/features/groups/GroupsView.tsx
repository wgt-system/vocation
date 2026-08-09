import { type FormEvent, useEffect, useState } from "react";

import {
  api,
  type OpportunityGroup,
  type OpportunityGroupPayload,
  type OpportunityListItem,
} from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

const blank: OpportunityGroupPayload = {
  name: "",
  description: "",
  group_type: "general",
};

const groupTypeLabels = {
  general: "General",
  application_wave: "Application Wave",
} as const;

function errorMessage(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback;
}

export function GroupsView() {
  const [groups, setGroups] = useState<OpportunityGroup[]>([]);
  const [opportunities, setOpportunities] = useState<OpportunityListItem[]>([]);
  const [selected, setSelected] = useState<OpportunityGroup | null>(null);
  const [form, setForm] = useState<OpportunityGroupPayload>(blank);
  const [editing, setEditing] = useState(false);
  const [memberToAdd, setMemberToAdd] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function reloadGroups(selectedId?: string) {
    setLoading(true);
    try {
      const next = await api.listGroups();
      setGroups(next);
      const nextId = selectedId ?? selected?.id;
      if (nextId) {
        const refreshed = next.find((item) => item.id === nextId);
        setSelected(refreshed ?? null);
      }
      setError("");
    } catch (reason) {
      setError(errorMessage(reason, "Groups konnten nicht geladen werden."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void Promise.all([api.listGroups(), api.listOpportunities()])
      .then(([nextGroups, nextOpportunities]) => {
        setGroups(nextGroups);
        setOpportunities(nextOpportunities);
        setError("");
      })
      .catch((reason) =>
        setError(errorMessage(reason, "Groups konnten nicht geladen werden.")),
      )
      .finally(() => setLoading(false));
  }, []);

  async function openGroup(id: string) {
    try {
      setSelected(await api.getGroup(id));
      setEditing(false);
      setError("");
    } catch (reason) {
      setError(errorMessage(reason, "Group konnte nicht geladen werden."));
    }
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    try {
      const next =
        editing && selected
          ? await api.editGroup(selected.id, form)
          : await api.createGroup(form);
      setForm(blank);
      setEditing(false);
      await reloadGroups(next.id);
      setSelected(next);
      setError("");
    } catch (reason) {
      setError(errorMessage(reason, "Group konnte nicht gespeichert werden."));
    }
  }

  async function removeGroup() {
    if (!selected) return;
    if (!window.confirm(`Group „${selected.name}“ wirklich löschen?`)) return;
    try {
      await api.deleteGroup(selected.id);
      setSelected(null);
      setEditing(false);
      await reloadGroups();
    } catch (reason) {
      setError(errorMessage(reason, "Group konnte nicht gelöscht werden."));
    }
  }

  async function addMember() {
    if (!selected || !memberToAdd) return;
    try {
      const next = await api.addGroupMembership(selected.id, memberToAdd);
      setSelected(next);
      setMemberToAdd("");
      setGroups((current) =>
        current.map((item) => (item.id === next.id ? next : item)),
      );
    } catch (reason) {
      setError(
        errorMessage(reason, "Opportunity konnte nicht hinzugefügt werden."),
      );
    }
  }

  async function removeMember(opportunityId: string) {
    if (!selected) return;
    try {
      const next = await api.removeGroupMembership(selected.id, opportunityId);
      setSelected(next);
      setGroups((current) =>
        current.map((item) => (item.id === next.id ? next : item)),
      );
    } catch (reason) {
      setError(
        errorMessage(reason, "Membership konnte nicht entfernt werden."),
      );
    }
  }

  async function moveMember(index: number, direction: number) {
    if (!selected) return;
    const target = index + direction;
    if (target < 0 || target >= selected.memberships.length) return;
    const ids = selected.memberships.map((item) => item.opportunity_id);
    [ids[index], ids[target]] = [ids[target], ids[index]];
    try {
      const next = await api.reorderGroup(selected.id, ids);
      setSelected(next);
      setGroups((current) =>
        current.map((item) => (item.id === next.id ? next : item)),
      );
    } catch (reason) {
      setError(
        errorMessage(reason, "Reihenfolge konnte nicht gespeichert werden."),
      );
    }
  }

  function beginEdit(group: OpportunityGroup) {
    setSelected(group);
    setEditing(true);
    setForm({
      name: group.name,
      description: group.description,
      group_type: group.group_type,
    });
  }

  const memberIds = new Set(
    selected?.memberships.map((item) => item.opportunity_id),
  );
  const available = opportunities.filter((item) => !memberIds.has(item.id));

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Vocation-owned organization</p>
          <h1>Groups &amp; Waves</h1>
        </div>
      </header>
      {loading && <Loading />}
      {error && <ErrorState message={error} />}
      <div className="groups-layout">
        <section className="panel">
          <h2>Groups</h2>
          {groups.length === 0 && !loading ? (
            <EmptyState>Noch keine Groups angelegt.</EmptyState>
          ) : (
            <div className="group-list">
              {groups.map((group) => (
                <button
                  className={`group-list-item ${selected?.id === group.id ? "active" : ""}`}
                  key={group.id}
                  onClick={() => void openGroup(group.id)}
                >
                  <strong>{group.name}</strong>
                  <small>
                    {groupTypeLabels[group.group_type]} ·{" "}
                    {group.memberships.length} Opportunities
                  </small>
                </button>
              ))}
            </div>
          )}
        </section>

        <form className="panel stack" onSubmit={save}>
          <h2>{editing ? "Group bearbeiten" : "Neue Group"}</h2>
          <label>
            Name
            <input
              value={form.name}
              onChange={(event) =>
                setForm({ ...form, name: event.target.value })
              }
              required
            />
          </label>
          <label>
            Beschreibung
            <textarea
              value={form.description ?? ""}
              onChange={(event) =>
                setForm({ ...form, description: event.target.value })
              }
            />
          </label>
          <label>
            Typ
            <select
              value={form.group_type}
              onChange={(event) =>
                setForm({
                  ...form,
                  group_type: event.target
                    .value as OpportunityGroupPayload["group_type"],
                })
              }
            >
              <option value="general">General</option>
              <option value="application_wave">Application Wave</option>
            </select>
          </label>
          <div className="actions">
            <button className="primary" type="submit">
              {editing ? "Speichern" : "Group erstellen"}
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
      </div>

      {selected && (
        <section className="panel group-detail">
          <header className="group-detail-header">
            <div>
              <p className="eyebrow">{groupTypeLabels[selected.group_type]}</p>
              <h2>{selected.name}</h2>
              {selected.description && <p>{selected.description}</p>}
            </div>
            <div className="actions">
              <button onClick={() => beginEdit(selected)}>Bearbeiten</button>
              <button onClick={() => void removeGroup()}>Löschen</button>
            </div>
          </header>
          <div className="group-membership-add">
            <label>
              Opportunity hinzufügen
              <select
                aria-label="Opportunity zur Group hinzufügen"
                value={memberToAdd}
                onChange={(event) => setMemberToAdd(event.target.value)}
              >
                <option value="">Auswählen …</option>
                {available.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.title} · {item.company_name}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              onClick={() => void addMember()}
              disabled={!memberToAdd}
            >
              Hinzufügen
            </button>
          </div>
          {selected.memberships.length === 0 ? (
            <EmptyState>Keine Opportunities in dieser Group.</EmptyState>
          ) : (
            <ol className="group-members">
              {selected.memberships.map((member, index) => (
                <li key={member.opportunity_id}>
                  <span>
                    <strong>{member.opportunity_title}</strong>
                    <small>{member.company_name}</small>
                  </span>
                  <div className="actions">
                    <button
                      aria-label={`${member.opportunity_title} nach oben`}
                      type="button"
                      disabled={index === 0}
                      onClick={() => void moveMember(index, -1)}
                    >
                      ↑
                    </button>
                    <button
                      aria-label={`${member.opportunity_title} nach unten`}
                      type="button"
                      disabled={index === selected.memberships.length - 1}
                      onClick={() => void moveMember(index, 1)}
                    >
                      ↓
                    </button>
                    <button
                      type="button"
                      onClick={() => void removeMember(member.opportunity_id)}
                    >
                      Entfernen
                    </button>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>
      )}
    </section>
  );
}
