# Gap Filling Prompt

Für die folgenden Vocation-Objekte fehlen oder widersprechen sich bestimmte Informationen:

{{GAP_SCOPE}}

Recherchiere ausschließlich die genannten Felder und liefere:
- Source,
- Beobachtungszeitpunkt,
- beobachteten Wert,
- Confidence oder Unsicherheit,
- Evidence Summary.


Ausgabeanforderungen:
- Antworte ausschließlich mit einem validen JSON-Objekt.
- Keine Markdown-Codeblöcke, keine Einleitung, keine Nachbemerkung.
- Verwende exakt `bundle_version: "1.0"`.
- Erfinde keine Vocation-IDs.
- Jede externe Information benötigt Source und Beobachtungszeitpunkt.
- Persönliche Assessments, Decisions, Tracking Status und Groups dürfen nicht verändert werden.
- Unsicherheit muss ausdrücklich markiert werden.
- Eine nicht erreichbare URL ist nicht automatisch eine endgültig geschlossene Opportunity.
