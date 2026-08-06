# Full Update Prompt

Aktualisiere den bestehenden Vocation-Bestand zum Stichtag {{AS_OF_DATE}}.

## Bekannter Bestand

{{VOCATION_CONTEXT_SNAPSHOT}}

## Aufgaben

- prüfe bekannte Postings auf Änderungen und Verfügbarkeit,
- finde relevante neue Opportunities im gleichen Suchraum,
- liefere nur neue oder geänderte Observations,
- erhalte bekannte Vocation-Referenzen,
- markiere mögliche Dubletten,
- überschreibe keine persönlichen Decisions.


Ausgabeanforderungen:
- Antworte ausschließlich mit einem validen JSON-Objekt.
- Keine Markdown-Codeblöcke, keine Einleitung, keine Nachbemerkung.
- Verwende exakt `bundle_version: "1.0"`.
- Erfinde keine Vocation-IDs.
- Jede externe Information benötigt Source und Beobachtungszeitpunkt.
- Persönliche Assessments, Decisions, Tracking Status und Groups dürfen nicht verändert werden.
- Unsicherheit muss ausdrücklich markiert werden.
- Eine nicht erreichbare URL ist nicht automatisch eine endgültig geschlossene Opportunity.
