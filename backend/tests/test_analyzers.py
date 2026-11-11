import asyncio

import httpx

from app.analyzer import content, performance, security, seo
from app.analyzer.seo import _score
from app.schemas import Check
from tests.conftest import good_site_handler


def by_name(result):
    return {c.name: c for c in result.checks}


def test_score_formula():
    checks = [Check(name="a", status="pass"), Check(name="b", status="warning"), Check(name="c", status="fail")]
    assert _score(checks) == 50  # (2+1+0) / 6
    assert _score([Check(name="a", status="info")]) == 100
    assert _score([]) == 0


def test_seo_good_page(mock_http):
    mock_http(good_site_handler)
    r = asyncio.run(seo.analyze("https://example.com"))
    assert r.error is None
    assert r.score == 100
    assert r.title.startswith("Beispiel")


def test_seo_empty_page_fails_key_checks(mock_http):
    mock_http(lambda req: httpx.Response(404 if req.url.path != "/" else 200, text="<html><body></body></html>"))
    r = asyncio.run(seo.analyze("https://example.com"))
    checks = by_name(r)
    assert checks["Title-Tag"].status == "fail"
    assert checks["Meta-Description"].status == "fail"
    assert checks["H1-Überschrift"].status == "fail"
    assert checks["Viewport Meta-Tag"].status == "fail"
    assert checks["robots.txt"].status == "warning"
    assert r.score < 30


def test_seo_title_length_boundaries(mock_http):
    def page(title):
        return lambda req: httpx.Response(200, text=f"<html><head><title>{title}</title></head></html>")

    for title, expected in [("x" * 29, "warning"), ("x" * 30, "pass"), ("x" * 60, "pass"), ("x" * 61, "warning")]:
        mock_http(page(title))
        assert by_name(asyncio.run(seo.analyze("https://example.com")))["Title-Tag"].status == expected


def test_seo_network_error_is_reported(mock_http):
    def boom(req):
        raise httpx.ConnectError("down")

    mock_http(boom)
    r = asyncio.run(seo.analyze("https://example.com"))
    assert r.score == 0 and r.error


def test_content_good_page(mock_http):
    mock_http(good_site_handler)
    r = asyncio.run(content.analyze("https://example.com"))
    assert r.error is None
    assert r.word_count >= 300
    assert r.internal_links == 3 and r.external_links == 1
    assert r.total_images == 1 and r.images_missing_alt == 0
    assert by_name(r)["Textmenge"].status == "pass"


def test_content_thin_page(mock_http):
    mock_http(lambda req: httpx.Response(200, text="<html><body><p>wenig Text</p></body></html>"))
    r = asyncio.run(content.analyze("https://example.com"))
    assert by_name(r)["Textmenge"].status == "fail"
    assert by_name(r)["Überschriftenstruktur"].status == "warning"


def test_security_all_headers_present(mock_http, monkeypatch):
    mock_http(good_site_handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: {"valid": True, "days_left": 90, "issuer": "LE"})
    r = asyncio.run(security.analyze("https://example.com"))
    assert r.error is None and r.is_https and r.ssl_valid is True and r.ssl_expiry_days == 90
    assert r.score == 100


def test_security_missing_headers_and_http(mock_http):
    mock_http(lambda req: httpx.Response(200, text="<html></html>"))
    r = asyncio.run(security.analyze("http://example.com"))
    checks = by_name(r)
    assert checks["HTTPS"].status == "fail"
    assert checks["HSTS (Strict-Transport-Security)"].status == "warning"
    assert r.is_https is False


def test_security_ssl_expiry_thresholds(mock_http, monkeypatch):
    mock_http(good_site_handler)
    for days, expected in [(5, "fail"), (20, "warning"), (60, "pass")]:
        monkeypatch.setattr(security, "_get_ssl_info", lambda h, d=days: {"valid": True, "days_left": d, "issuer": "LE"})
        r = asyncio.run(security.analyze("https://example.com"))
        assert by_name(r)["SSL-Zertifikat"].status == expected


def test_security_invalid_certificate(mock_http, monkeypatch):
    mock_http(good_site_handler)
    monkeypatch.setattr(security, "_get_ssl_info", lambda h: {"valid": False, "days_left": None, "issuer": None, "error": "Zertifikat ungültig"})
    r = asyncio.run(security.analyze("https://example.com"))
    assert by_name(r)["SSL-Zertifikat"].status == "fail"


def test_security_ssl_check_refuses_internal_host(dns):
    dns["internal.test"] = "10.0.0.1"
    info = security._get_ssl_info("internal.test")
    assert info["valid"] is None and info["error"]


def test_performance_parses_pagespeed(mock_http):
    mock_http(good_site_handler)
    r = asyncio.run(performance.analyze("https://example.com"))
    assert r.error is None
    assert r.score == 90
    statuses = {m.name: m.status for m in r.metrics}
    assert statuses["First Contentful Paint (FCP)"] == "good"
    assert statuses["Cumulative Layout Shift (CLS)"] == "good"


def test_performance_api_error(mock_http):
    mock_http(lambda req: httpx.Response(429, json={}))
    r = asyncio.run(performance.analyze("https://example.com"))
    assert r.score is None and "429" in r.error


def test_performance_metric_thresholds():
    assert performance._metric_status(1800, 1800, 3000) == "good"
    assert performance._metric_status(3000, 1800, 3000) == "needs-improvement"
    assert performance._metric_status(3001, 1800, 3000) == "poor"
    assert performance._metric_status(None, 1800, 3000) == "info"
