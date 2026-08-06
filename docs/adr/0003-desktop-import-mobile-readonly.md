# ADR-0003: Desktop-Import, mobile Nutzung zunächst read-only

**Status:** Accepted

## Entscheidung

Prompt-Erzeugung und JSON-Import sind Desktop-Funktionen. Mobile Clients konsumieren zunächst ausschließlich Read Models.

## Konsequenzen

- mobile Verträge enthalten keine Import-Commands,
- iOS kann deutlich später implementiert werden,
- Desktop bleibt Source of Record.
