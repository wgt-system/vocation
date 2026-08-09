# ADR-0008: Opaque Correlation References für Research Update Bundle 2.0

**Status:** Accepted

## Kontext

Research Bundle 1.0 bleibt ein initial-only Contract. Kontrollierte Updates benötigen eine Zuordnung zwischen dem von Vocation ausgegebenen Prompt Context Snapshot und dem zurückgegebenen Research, ohne interne Vocation IDs zu veröffentlichen oder über Prompt Runs hinweg stabile externe Identitäten zu versprechen.

## Entscheidung

Research Update Bundle 2.0 verwendet den verpflichtenden `prompt_context_ref` und Vocation-ausgestellte opaque `correlation_ref`-Werte. Eine Correlation Reference wird ausschließlich von Vocation erzeugt, ist nur für den ausstellenden Prompt Context Snapshot gültig und mappt genau auf ein bestehendes Company-, Opportunity- oder Posting-Objekt. Research darf sie nur echoen und darf keine neuen oder erfundenen References erzeugen. Correlation References müssen zwischen Prompt Runs nicht stabil sein.

Bekannte Subjects werden mit bundle-lokaler ID und Correlation Reference dargestellt; neue Subjects besitzen keine Correlation Reference und liefern die normalen Creation-/Evidence-Felder. Bundle-lokale IDs bleiben die einzigen internen Referenzen im Bundle. Die Werte sind opaque Strings ohne vorgeschriebene Präfix- oder Typsemantik.

## Konsequenzen

- Interne Company-, Opportunity- und Posting-IDs sind kein Bestandteil des veröffentlichten Update Contracts.
- `prompt_context_ref` bindet jedes Update an genau einen Snapshot.
- Scope- und Correlation-Fehler sind Blocker vor Domain-Mutation.
- Ownership-Beziehungen dürfen durch eine Correlation Reference nicht geändert werden.
- Deterministische Posting-Identität bleibt unabhängig prüfbar; ein Widerspruch erzeugt `IDENTITY_CONFLICT`.
- Die Entscheidung definiert nur Contract und Tests. Update-Importer, Identity Resolver und DuplicateCase-Persistenz bleiben spätere Arbeit.
