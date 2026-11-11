import httpx
import pytest
from fastapi.testclient import TestClient

from app import rate_limit
from app.analyzer import security, seo
from app.main import app
from tests.conftest import good_site_handler

client = TestClient(app)

SSL_OK = {"valid": True, "days_left": 90, "issuer": "LE"}


def analyze(url, **kw):
    return client.post("/api/analyze", json={"url": url}, **kw)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_successful_analysis(mock_http, monkeypatch):
    mock_http(good_site_handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: SSL_OK)
    r = analyze("example.com")  # scheme is added automatically
    assert r.status_code == 200
    j = r.json()
    assert j["url"] == "https://example.com"
    assert j["http_status"] == 200
    assert j["seo"]["score"] == 100 and j["security"]["score"] == 100
    assert j["performance"]["score"] == 90
    # seo*.35 + perf*.35 + security*.20 + content*.10
    assert j["overall_score"] == round(35 + 31.5 + 20 + j["content"]["score"] * 0.1)


def test_one_failing_analyzer_does_not_break_the_rest(mock_http, monkeypatch):
    mock_http(good_site_handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: SSL_OK)

    async def boom(url):
        raise RuntimeError("kaputt")

    monkeypatch.setattr(seo, "analyze", boom)
    j = analyze("https://example.com").json()
    assert j["seo"]["error"] == "kaputt" and j["seo"]["score"] == 0
    assert j["security"]["score"] == 100


def test_missing_performance_counts_as_50(mock_http, monkeypatch):
    def handler(req):
        if req.url.host == "www.googleapis.com":
            return httpx.Response(500)
        return good_site_handler(req)

    mock_http(handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: SSL_OK)
    j = analyze("https://example.com").json()
    assert j["performance"]["score"] is None
    expected = round(j["seo"]["score"] * 0.35 + 50 * 0.35 + j["security"]["score"] * 0.2 + j["content"]["score"] * 0.1)
    assert j["overall_score"] == expected


def test_http_error_page_is_analyzed_with_status(mock_http, monkeypatch):
    def handler(req):
        if req.url.path == "/" and req.url.host == "example.com":
            return httpx.Response(404, text="<html><body>nope</body></html>")
        return good_site_handler(req)

    mock_http(handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: SSL_OK)
    r = analyze("https://example.com")
    assert r.status_code == 200 and r.json()["http_status"] == 404


@pytest.mark.parametrize("url", ["http://localhost", "127.0.0.1", "http://169.254.169.254/latest", "http://10.0.0.1", "http://[::1]"])
def test_internal_targets_are_rejected_with_400(url):
    r = analyze(url)
    assert r.status_code == 400
    assert "interne" in r.json()["detail"]


def test_bad_port_and_credentials_rejected(dns):
    assert analyze("https://example.com:22").status_code == 400
    assert analyze("https://user:pw@example.com").status_code == 400


def test_unknown_domain_message(dns):
    dns["gone.test"] = None
    r = analyze("https://gone.test")
    assert r.status_code == 400 and "Domain" in r.json()["detail"]


def test_redirect_to_internal_address_returns_400(mock_http, dns):
    dns["evil.test"] = "10.0.0.9"
    mock_http(lambda req: httpx.Response(302, headers={"location": "http://evil.test/"}))
    r = analyze("https://example.com")
    assert r.status_code == 400


@pytest.mark.parametrize("exc, text", [
    (httpx.ConnectTimeout("t"), "Timeout"),
    (httpx.ConnectError("[SSL: CERTIFICATE_VERIFY_FAILED] bad"), "SSL-Zertifikat"),
    (httpx.ConnectError("refused"), "nicht erreichbar"),
    (httpx.ReadError("reset"), "nicht abgerufen"),
])
def test_unreachable_site_returns_502(mock_http, exc, text):
    def handler(req):
        raise exc

    mock_http(handler)
    r = analyze("https://example.com")
    assert r.status_code == 502
    assert text in r.json()["detail"]


def test_redirect_loop_returns_502(mock_http):
    mock_http(lambda req: httpx.Response(302, headers={"location": str(req.url)}))
    r = analyze("https://example.com")
    assert r.status_code == 502 and "Endlosschleife" in r.json()["detail"]


def test_rate_limit_applies_to_analyze_but_not_health(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 2)
    headers = {"x-real-ip": "7.7.7.7"}
    assert analyze("http://localhost", headers=headers).status_code == 400
    assert analyze("http://localhost", headers=headers).status_code == 400
    r = analyze("http://localhost", headers=headers)
    assert r.status_code == 429 and "Retry-After" in r.headers
    assert client.get("/api/health", headers=headers).status_code == 200
    assert analyze("http://localhost", headers={"x-real-ip": "8.8.8.8"}).status_code == 400
