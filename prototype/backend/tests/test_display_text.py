"""Tests for display_text endpoint."""

from fastapi.testclient import TestClient

from api import init_app

client = TestClient(init_app())


def test_display_text_round_trip() -> None:
    """Ensure text can be set and retrieved."""

    resp = client.post("/api/display_text", json={"text": "Hello"})
    assert resp.status_code == 200
    assert resp.json() == {"success": True}

    resp = client.get("/api/display_text")
    assert resp.status_code == 200
    assert resp.json() == {"text": "Hello"}
