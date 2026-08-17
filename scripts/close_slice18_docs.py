from pathlib import Path

ADDITIONS = {
    "docs/07_APPLICATION_DESIGN.md": """

## Slice 18 – DuplicateCase Resolution (implementiert auf `dev`)

`ResolveDuplicateCase` ist als explizite Vocation-Nutzeraktion implementiert. Ein bestehender Opportunity- oder Posting-`DuplicateCase` wird über einen internen Review-Read-Path mit Subject-Summaries, Evidence und Source-Reference-Summaries dargestellt. `POST /api/duplicate-cases/{case_id}/decisions` erzeugt genau eine append-only `DuplicateDecision` mit Outcome `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` oder `keep_unresolved`, nichtleerem Grund, Sequenz und Entscheidungszeitpunkt. Die neueste Decision ist die aktuelle Review-Sicht; eine abweichende spätere Decision korrigiert diese Sicht, ohne Historie zu überschreiben. Dasselbe aktuelle Outcome wird als Konflikt abgelehnt.

`confirmed_duplicate` ist ausschließlich eine Klassifikation. Slice 18 führt keinen Merge, keine Löschung, kein Re-Parenting und keine Referenzumschreibung aus. Research-/Availability-Imports, Groups/Waves, ApplicationCase-Lifecycle und Published Contracts erzeugen oder verändern keine Duplicate Decisions.
""",
    "docs/09_READ_MODELS.md": """

## 14. DuplicateCaseReview (implemented)

Interner, nicht persistierter Review-Read-Model für bestehende Opportunity- und Posting-`DuplicateCase`s. Er enthält die stabile Case-ID, Subject Type, je Subject eine lesbare Summary, Evidence Summary, optionale Import-Confidence, Source-Reference-Summaries, Created At, aktuelle Duplicate Decision, vollständige append-only Decision History sowie `is_reviewed` und `is_resolved`.

Ohne Decision ist ein Case ungeprüft und unresolved. `keep_unresolved` ist geprüft, aber unresolved; die anderen drei Outcomes sind für den Review resolved. Source URLs werden in der `Dubletten`-Ansicht nur als Review-Kontext angezeigt und nicht als direkte Navigation verwendet. Das Read Model besitzt keine Merge-, Delete- oder Published-Contract-Semantik.
""",
    "docs/10_ARCHITECTURE.md": """

## 15. Duplicate Case Resolution

Slice 18 ergänzt die bestehende DuplicateCase-Evidence um eine getrennte append-only `DuplicateDecision`-Historie. Alembic `0013` persistiert Entscheidungen mit einer eindeutigen monotonen Sequence pro Case und geschlossenem Outcome-Vokabular. Domain/Application leiten aktuelle Review-Sicht ausschließlich aus der letzten Decision ab; bestehende DuplicateCase-Evidence bleibt unverändert.

Die interne Kette lautet: `DuplicateCaseService` → `SqlAlchemyDuplicateCaseRepository` → `duplicate_case_decisions` → interne `/api/duplicate-cases`-Read-/Decision-Routen → typed React client → `Dubletten`-Ansicht. Subject-/Source-Summaries sind reine Read-Model-Daten. Es gibt keine Merge-Engine und keine Mutation der beteiligten Opportunity-/Posting-Identitäten oder ihrer Assessments, Decisions, Groups, ApplicationCases, Documents oder Published References.
""",
    "docs/11_ACCEPTANCE_TESTS.md": """

## AT-106 Duplicate Decision History and Isolation

Ein bestehender Opportunity- oder Posting-DuplicateCase kann nur durch explizite Nutzeraktion mit `confirmed_duplicate`, `confirmed_distinct`, `related_but_distinct` oder `keep_unresolved` und nichtleerem Grund entschieden werden. Jede Decision wird mit fortlaufender Sequence append-only gespeichert; eine abweichende spätere Decision wird aktuell, ohne ältere Decisions zu verändern. Dasselbe aktuelle Outcome wird als Konflikt abgelehnt. Research-/Availability-Imports sowie persönliche Opportunity-Zustände bleiben davon unverändert.

## AT-107 Duplicate Review API and UI Without Merge

Die internen `/api/duplicate-cases`-Routen liefern Opportunity- und Posting-Cases mit lesbaren Subject-/Source-Summaries, aktueller Decision und Historie. Die React-Ansicht `Dubletten` filtert offen/entschieden/alle, verlangt einen Entscheidungsgrund und zeigt Evidence-URLs nur als nicht klickbaren Review-Kontext. `confirmed_duplicate` erzeugt weder Merge, Delete, Re-Parenting noch sonstige Identitätsmutation; es gibt keine Merge-/Delete-Controls und keine Änderung an Published Opportunity Overview 1.0 oder Published Map Projection 1.0.
""",
}

PLAN_SECTION = """
## Slice 18 – Duplicate Case Resolution (implementiert auf `dev`)

Vocation kann bestehende Opportunity- und Posting-DuplicateCases jetzt explizit und historisiert reviewen. Implementiert sind `DuplicateDecision` mit den vier eingefrorenen Outcomes und nichtleerem Grund, Alembic `0013`, append-only SQLAlchemy-Persistenz, aktuelle Review-Sicht aus der letzten Decision, interne `/api/duplicate-cases`-Read-/Decision-Routen, generierte TypeScript-API-Typen sowie die React-Ansicht `Dubletten` mit offenen/entschiedenen/allen Fällen und vollständiger Decision History.

`confirmed_duplicate` bleibt reine Klassifikation. Slice 18 führt keinen Merge, keine Löschung, kein Canonical-Survivor-Modell, kein Re-Parenting und keine Übertragung von Assessments, Decisions, Groups/Waves, ApplicationCases, ApplicationMaterials oder ApplicationDocuments aus. Research-/Availability-Imports verändern Duplicate Decisions nicht. Published Opportunity Overview 1.0 und Published Map Projection 1.0 bleiben unverändert. Eine spätere Merge-Capability benötigt eine eigene explizit eingefrorene Semantik.

"""

for filename, addition in ADDITIONS.items():
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    heading = addition.strip().splitlines()[0]
    if heading not in text:
        path.write_text(text.rstrip() + addition + "\n", encoding="utf-8")

plan = Path("docs/13_IMPLEMENTATION_PLAN.md")
text = plan.read_text(encoding="utf-8")
heading = "## Slice 18 – Duplicate Case Resolution (implementiert auf `dev`)"
if heading not in text:
    marker = "## Cross-cutting Migration – Orientation Integration"
    if marker in text:
        text = text.replace(marker, PLAN_SECTION + marker, 1)
    else:
        text = text.rstrip() + "\n\n" + PLAN_SECTION
    plan.write_text(text, encoding="utf-8")
