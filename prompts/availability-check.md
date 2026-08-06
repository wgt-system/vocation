# Availability Check Prompt

Prüfe ausschließlich die Erreichbarkeit und explizite Verfügbarkeit der folgenden Postings:

{{POSTING_SCOPE}}

Unterscheide:
- reachable,
- explicitly_available,
- explicitly_unavailable,
- not_found,
- temporarily_unreachable,
- unknown.

Bewerte eine Opportunity nicht allein deshalb als geschlossen, weil eine einzelne URL nicht erreichbar ist.


Ausgabeanforderungen:
- Antworte ausschließlich mit einem validen JSON-Objekt.
- Keine Markdown-Codeblöcke, keine Einleitung, keine Nachbemerkung.
- Verwende exakt `bundle_version: "1.0"`.
- Erfinde keine Vocation-IDs.
- Jede externe Information benötigt Source und Beobachtungszeitpunkt.
- Persönliche Assessments, Decisions, Tracking Status und Groups dürfen nicht verändert werden.
- Unsicherheit muss ausdrücklich markiert werden.
- Eine nicht erreichbare URL ist nicht automatisch eine endgültig geschlossene Opportunity.
