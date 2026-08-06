import { useEffect, useState } from "react";

import { api, type OpportunityListItem } from "../../api/client";
import { EmptyState, ErrorState, Loading } from "../../components/AsyncState";

export function OpportunityList({ refreshToken, onSelect }: { refreshToken: number; onSelect: (id: string) => void }) {
  const [items, setItems] = useState<OpportunityListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    setLoading(true);
    api.listOpportunities().then(setItems).catch((reason) => setError(reason instanceof Error ? reason.message : "Opportunities konnten nicht geladen werden.")).finally(() => setLoading(false));
  }, [refreshToken]);

  return (
    <section>
      <header className="page-header"><div><p className="eyebrow">Persönlicher Stellenmarkt</p><h1>Opportunities</h1></div><span className="count-badge">{items.length}</span></header>
      {loading && <Loading />}{error && <ErrorState message={error} />}
      {!loading && !error && items.length === 0 && <EmptyState><h2>Noch keine Opportunities</h2><p>Erzeuge einen Research Prompt und importiere anschließend das JSON Bundle.</p></EmptyState>}
      <div className="opportunity-grid">
        {items.map((item) => (
          <button className="opportunity-card" key={item.id} onClick={() => onSelect(item.id)}>
            <span className="eyebrow">{item.company_name}</span><strong>{item.title}</strong><span>{item.locations.join(" · ") || "Arbeitsort unbekannt"}</span><small>{item.posting_count} Posting · {item.assessment_count} Assessment</small>
          </button>
        ))}
      </div>
    </section>
  );
}
