from fastapi.testclient import TestClient

from app import newsletter
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
