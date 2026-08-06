# Initial Market Research Prompt

Führe eine aktuelle Stellenrecherche für den unten angegebenen Scope durch.

## Suchprofil

{{SEARCH_PROFILE}}

## Region und Einschränkungen

{{REGION_AND_CONSTRAINTS}}

## Gewünschter Umfang

{{RESEARCH_TARGET}}

## Stichtag

{{AS_OF_DATE}}

Recherchiere konkrete aktive Stellenanzeigen und liefere belastbare Quellen. Trenne Company, Opportunity und Posting. Markiere Unsicherheiten.


Ausgabeanforderungen:
- Antworte ausschließlich mit einem validen JSON-Objekt.
- Keine Markdown-Codeblöcke, keine Einleitung, keine Nachbemerkung.
- Verwende exakt `bundle_version: "1.0"`.
- Erfinde keine Vocation-IDs.
- Jede externe Information benötigt Source und Beobachtungszeitpunkt.
- Persönliche Assessments, Decisions, Tracking Status und Groups dürfen nicht verändert werden.
- Unsicherheit muss ausdrücklich markiert werden.
- Eine nicht erreichbare URL ist nicht automatisch eine endgültig geschlossene Opportunity.
