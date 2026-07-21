"""Smoke test for the health endpoint (DB-independent)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "great-energy-field-backend"
    # database may be "ok" or "unavailable" depending on local DB; both are valid
    assert body["database"] in {"ok", "unavailable"}


def test_root_ok() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "great-energy-field-backend"
