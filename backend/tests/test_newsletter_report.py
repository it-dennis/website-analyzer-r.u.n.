from fastapi.testclient import TestClient

from app import brevo, newsletter
from app.main import app


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr(newsletter, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(newsletter, "FILE", str(tmp_path / "newsletter.csv"))
    return TestClient(app)


def test_subscribe_requires_consent_and_valid_email(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    assert c.post("/api/subscribe", json={"email": "a@b.de", "consent": False}).status_code == 422
    assert c.post("/api/subscribe", json={"email": "kein-mail", "consent": True}).status_code == 422


def test_subscribe_honeypot_writes_nothing(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    r = c.post("/api/subscribe", json={"email": "bot@b.de", "consent": True, "website": "x"})
    assert r.status_code == 200
    assert not newsletter.contains("bot@b.de")


def test_subscribe_then_contains_and_csv_injection_is_neutralized(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    r = c.post("/api/subscribe", json={"email": "a@b.de", "consent": True, "domain": "=HYPERLINK(1)"})
    assert r.status_code == 200
    assert newsletter.contains("a@b.de")
    row = (tmp_path / "newsletter.csv").read_text(encoding="utf-8")
    assert ";=HYPERLINK" not in row and "unbestaetigt" in row


def test_report_needs_subscription():
    c = TestClient(app)
    r = c.post("/api/report", json={"url": "beispiel.de", "email": "nie-eingetragen@example.org"})
    assert r.status_code == 403


def test_subscribe_calls_brevo_and_survives_its_failure(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    calls = []

    async def fake(email):
        calls.append(email)
        return False  # Brevo down

    monkeypatch.setattr(brevo, "double_optin", fake)
    r = c.post("/api/subscribe", json={"email": "x@y.de", "consent": True})
    assert r.status_code == 200 and calls == ["x@y.de"]
    assert newsletter.contains("x@y.de")


def test_brevo_disabled_without_key(monkeypatch):
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    import asyncio
    assert asyncio.run(brevo.double_optin("a@b.de")) is False
