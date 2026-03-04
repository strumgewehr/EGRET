"""Pytest fixtures: test client and DB session."""
import os
import pytest
from fastapi.testclient import TestClient

# Use in-memory SQLite for tests to avoid requiring Postgres in CI
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
