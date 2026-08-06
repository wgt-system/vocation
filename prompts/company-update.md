# Company Update Prompt

Aktualisiere ausschließlich die folgenden Companies und zugehörigen Opportunities:

{{COMPANY_SCOPE}}

Prüfe:
- neue oder entfernte Postings,
- Änderungen an Aufgaben, Technologien, Standort und Seniority,
- neue relevante Opportunities,
- Availability und Veröffentlichungsdaten.

Außerhalb dieses Scopes liegende Funde dürfen nur als Warning erwähnt werden.


Ausgabeanforderungen:
- Antworte ausschließlich mit einem validen JSON-Objekt.
- Keine Markdown-Codeblöcke, keine Einleitung, keine Nachbemerkung.
- Verwende exakt `bundle_version: "1.0"`.
- Erfinde keine Vocation-IDs.
- Jede externe Information benötigt Source und Beobachtungszeitpunkt.
- Persönliche Assessments, Decisions, Tracking Status und Groups dürfen nicht verändert werden.
- Unsicherheit muss ausdrücklich markiert werden.
- Eine nicht erreichbare URL ist nicht automatisch eine endgültig geschlossene Opportunity.
