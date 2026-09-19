from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from roombook.deps import get_now
from roombook.main import create_app

# Monday 26 October 2026, 08:00 UTC: the start of the sample data's fortnight.
NOW = datetime(2026, 10, 26, 8, 0, tzinfo=UTC)


@pytest.fixture
def client(tmp_path):
    """An API client backed by a freshly seeded database that only this test uses."""
    app = create_app(tmp_path / "roombook.db")
    app.dependency_overrides[get_now] = lambda: NOW
    # Entering the client runs the app's startup, which builds and seeds the database.
    with TestClient(app) as client:
        yield client
