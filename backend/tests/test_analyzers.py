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


def test_alt_rule_empty_alt_is_decorative(mock_http):
    html = '<html lang="de"><body><img src="a.png" alt=""><img src="b.png" alt="B"><img src="c.png"></body></html>'
    mock_http(lambda req: httpx.Response(200, text=html))
    r = asyncio.run(content.analyze("https://example.com"))
    assert r.total_images == 3 and r.images_missing_alt == 1


def test_alt_not_double_counted_in_content_score(mock_http):
    html = "<html><body><h2>x</h2>" + '<img src="a.png">' * 4 + "<a href='/a'>a</a>" * 3 + "<p>" + "wort " * 320 + "</p></body></html>"
    mock_http(lambda req: httpx.Response(200, text=html))
    r = asyncio.run(content.analyze("https://example.com"))
    assert by_name(r)["Bilder Alt-Texte"].status == "info"
    assert r.score == 100


def test_robots_follows_redirect_and_reads_sitemap_directive(mock_http):
    def handler(req):
        if req.url.path == "/robots.txt" and req.url.host == "example.com":
            return httpx.Response(301, headers={"location": "https://cdn.example.org/robots.txt"})
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow:\nSitemap: https://example.com/map.xml")
        if req.url.path == "/map.xml":
            return httpx.Response(200, text="<urlset></urlset>")
        return httpx.Response(200, text="<html><body></body></html>") if req.url.path == "/" else httpx.Response(404)

    mock_http(handler)
    checks = by_name(asyncio.run(seo.analyze("https://example.com")))
    assert checks["robots.txt"].status == "pass"
    assert checks["sitemap.xml"].status == "pass"


def test_robots_disallow_all_fails(mock_http):
    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        return httpx.Response(200, text="<html></html>")

    mock_http(handler)
    assert by_name(asyncio.run(seo.analyze("https://example.com")))["robots.txt"].status == "fail"


def test_robots_and_sitemap_html_are_not_accepted(mock_http):
    mock_http(lambda req: httpx.Response(200, text="<!doctype html><html><body>Willkommen</body></html>"))
    checks = by_name(asyncio.run(seo.analyze("https://example.com")))
    assert checks["robots.txt"].status == "warning"
    assert checks["sitemap.xml"].status == "warning"


def test_seo_uses_final_host_for_robots(mock_http):
    seen = []

    def handler(req):
        seen.append((req.url.host, req.url.path))
        if req.url.host == "example.com" and req.url.path == "/":
            return httpx.Response(301, headers={"location": "https://www.example.com/"})
        return httpx.Response(200, text="<html></html>")

    mock_http(handler)
    asyncio.run(seo.analyze("https://example.com/"))
    assert ("www.example.com", "/robots.txt") in seen


def test_js_rendered_page_gets_hint(mock_http):
    html = '<html><body><div id="root"></div><script src="/a.js"></script><noscript>Please enable JavaScript</noscript></body></html>'
    mock_http(lambda req: httpx.Response(200, text=html))
    assert "JavaScript-Inhalte" in by_name(asyncio.run(seo.analyze("https://example.com")))
    assert "JavaScript-Inhalte" in by_name(asyncio.run(content.analyze("https://example.com")))


def test_static_page_gets_no_js_hint(mock_http):
    mock_http(good_site_handler)
    assert "JavaScript-Inhalte" not in by_name(asyncio.run(seo.analyze("https://example.com")))


def test_security_header_values_are_judged():
    checks = by_name_list(security._evaluate_headers({
        "strict-transport-security": "max-age=300",
        "x-frame-options": "ALLOW-FROM x",
        "x-content-type-options": "sniff",
        "referrer-policy": "unsafe-url",
        "content-security-policy": "script-src 'self' 'unsafe-inline'",
    }))
    assert all(c.status == "warning" for c in checks.values())


def test_security_header_frame_ancestors_and_nonce_are_accepted():
    checks = by_name_list(security._evaluate_headers({
        "strict-transport-security": 'max-age=63072000; includeSubDomains',
        "content-security-policy": "script-src 'nonce-abc' 'unsafe-inline'; frame-ancestors 'none'",
        "x-content-type-options": "nosniff",
        "referrer-policy": "strict-origin-when-cross-origin",
    }))
    assert all(c.status == "pass" for c in checks.values())


def by_name_list(checks):
    return {c.name: c for c in checks}


def test_performance_requests_all_categories(mock_http):
    seen = {}

    def handler(req):
        seen["q"] = req.url.params.get_list("category")
        return good_site_handler(req)

    mock_http(handler)
    asyncio.run(performance.analyze("https://example.com"))
    assert set(seen["q"]) == {"performance", "accessibility", "best-practices", "seo"}
