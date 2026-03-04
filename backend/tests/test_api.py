"""API endpoint tests. Use TestClient; DB may be SQLite in-memory or real Postgres from env."""
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "service" in data
    assert "News Sentiment" in data.get("service", "")


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


def test_docs_available(client: TestClient):
    r = client.get("/docs")
    assert r.status_code == 200
