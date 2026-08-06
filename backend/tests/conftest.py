from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from vocation.api.app import create_app
from vocation.config import get_settings


@pytest.fixture
def app(tmp_path: Path):
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{(tmp_path / 'vocation-test.db').as_posix()}",
        frontend_dist=tmp_path / "no-frontend",
    )
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client
