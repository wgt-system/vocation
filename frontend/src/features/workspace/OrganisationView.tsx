import { GroupsView } from "../groups/GroupsView";

export function OrganisationView() {
  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Bewerbungsplanung</p>
          <h1>Bewerbungen</h1>
          <p className="page-description">
            Ordne interessante Stellen in Sammlungen und Bewerbungsphasen. Der
            eigentliche Bewerbungsfall und die Unterlagen werden hier in den
            nächsten Ausbauschritten zusammengeführt.
          </p>
        </div>
      </header>
      <GroupsView />
    </section>
  );
}
