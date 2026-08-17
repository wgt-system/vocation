from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from tests.test_imports import valid_bundle
from vocation.application.external_navigation import BrowserOpenError, ExternalNavigationService
from vocation.infrastructure.browser_adapter import SystemBrowserAdapter
from vocation.infrastructure.external_link_repository import SqlAlchemyExternalLinkRepository
from vocation.infrastructure.models import AvailabilityObservationModel, PostingModel, SourceReferenceModel


def seed_import(client) -> tuple[str, str]:
    report = client.post("/api/imports/text", json={"content": json.dumps(valid_bundle())}).json()
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    with client.app.state.database.session_factory() as session:
        posting_id = session.scalar(select(PostingModel.id).where(PostingModel.opportunity_id == opportunity_id))
    return report["import_id"], posting_id


def test_sql_external_link_adapter_derives_source_and_availability(client) -> None:
    import_id, posting_id = seed_import(client)
    with client.app.state.database.session_factory.begin() as session:
        session.add(
            AvailabilityObservationModel(
                id="external-link-availability",
                import_id=import_id,
                bundle_local_id="external-link-availability",
                posting_id=posting_id,
                result="explicitly_available",
                observed_at=datetime(2026, 8, 9, 12, 0),
                recorded_at=datetime(2026, 8, 9, 12, 1),
                evidence_summary="Listing is active",
            )
        )
    repository = SqlAlchemyExternalLinkRepository(
        client.app.state.database.session_factory,
        clock=lambda: datetime(2026, 8, 10, tzinfo=UTC),
    )
    links = repository.links_for_opportunity(client.get("/api/opportunities").json()[0]["id"])
    assert links is not None
    assert links[0].posting_id == posting_id
    assert links[0].source_name == "Example Careers"
    assert links[0].source_type == "company_careers"
    assert links[0].url == "https://example.com/careers/junior-dev"
    assert links[0].display_label == "Original posting"
    assert links[0].availability == "available"
    assert repository.links_for_posting("missing", posting_id) is None


class FakeBrowser:
    def __init__(self) -> None:
        self.urls: list[str] = []

    def open(self, url: str) -> None:
        self.urls.append(url)


def test_external_link_http_get_and_explicit_post_open(client) -> None:
    _, posting_id = seed_import(client)
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    links = client.get(f"/api/external-links/opportunities/{opportunity_id}")
    assert links.status_code == 200
    assert len(links.json()) == 1
    assert links.json()[0]["posting_id"] == posting_id
    assert links.json()[0]["preferred"] is True

    browser = FakeBrowser()
    current = client.app.state.external_navigation_service
    client.app.state.external_navigation_service = ExternalNavigationService(current.repository, browser)
    opened = client.post(
        f"/api/external-links/opportunities/{opportunity_id}/open",
        json={"posting_id": posting_id},
    )
    assert opened.status_code == 200
    assert opened.json()["posting_id"] == posting_id
    assert browser.urls == ["https://example.com/careers/junior-dev"]


def test_external_link_http_errors_and_invalid_explicit_link_does_not_fallback(client) -> None:
    _, posting_id = seed_import(client)
    opportunity_id = client.get("/api/opportunities").json()[0]["id"]
    assert client.get("/api/external-links/opportunities/missing").status_code == 404
    assert client.post(f"/api/external-links/opportunities/{opportunity_id}/open", json={"posting_id": "missing"}).status_code == 404

    with client.app.state.database.session_factory.begin() as session:
        posting = session.get(PostingModel, posting_id)
        reference = session.scalar(select(SourceReferenceModel).where(SourceReferenceModel.id == posting.source_reference_id))
        reference.url = "http://not-openable.example/job"
    assert client.get(f"/api/external-links/opportunities/{opportunity_id}").json() == []
    assert client.post(f"/api/external-links/opportunities/{opportunity_id}/open", json={"posting_id": posting_id}).status_code == 409


@pytest.mark.parametrize("opener", [lambda _url: False, lambda _url: (_ for _ in ()).throw(RuntimeError("failed"))])
def test_system_browser_adapter_maps_false_and_exceptions(opener) -> None:
    with pytest.raises(BrowserOpenError):
        SystemBrowserAdapter(opener).open("https://example.com")
