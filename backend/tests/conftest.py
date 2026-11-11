import socket

import httpx
import pytest

from app import rate_limit

_REAL_CLIENT = httpx.AsyncClient
PUBLIC_IP = "93.184.216.34"


@pytest.fixture(autouse=True)
def _reset_rate_limit(monkeypatch):
    rate_limit._hits.clear()
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 1000)
    monkeypatch.setattr(rate_limit, "PER_HOUR", 1000)


@pytest.fixture
def dns(monkeypatch):
    """Fake DNS: hostname -> IP (default public). A value of None means 'does not resolve'."""
    table: dict[str, str | None] = {}

    def fake_getaddrinfo(host, port, *args, **kwargs):
        ip = table.get(host, PUBLIC_IP)
        if ip is None:
            raise socket.gaierror("not found")
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        return [(family, socket.SOCK_STREAM, 6, "", (ip, port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    return table


@pytest.fixture
def mock_http(monkeypatch, dns):
    """Route every httpx.AsyncClient through a MockTransport; event hooks (SSRF guard) still run."""

    def install(handler):
        def factory(*args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            return _REAL_CLIENT(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", factory)

    return install


GOOD_HTML = """<!doctype html>
<html lang="de"><head>
<title>Beispiel Webseite mit gutem Titel für Tests</title>
<meta name="description" content="{desc}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://example.com/">
<meta property="og:title" content="t"><meta property="og:description" content="d"><meta property="og:image" content="i">
<script type="application/ld+json">{{}}</script>
</head><body>
<h1>Hauptüberschrift</h1><h2>Unterpunkt</h2><h3>Detail</h3>
<img src="a.png" alt="Bild A">
<a href="/a">a</a><a href="/b">b</a><a href="https://example.com/c">c</a><a href="https://other.org/">x</a>
<p>{text}</p>
</body></html>""".format(desc="d" * 140, text=" ".join(["wort"] * 320))


def good_site_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path in ("/robots.txt", "/sitemap.xml"):
        return httpx.Response(200, text="ok")
    if request.url.host == "www.googleapis.com":
        audits = {
            "first-contentful-paint": {"numericValue": 1000, "displayValue": "1,0 s"},
            "largest-contentful-paint": {"numericValue": 2000, "displayValue": "2,0 s"},
            "total-blocking-time": {"numericValue": 100, "displayValue": "100 ms"},
            "cumulative-layout-shift": {"numericValue": 0.05, "displayValue": "0,05"},
            "speed-index": {"displayValue": "1,5 s"},
        }
        cats = {k: {"score": 0.9} for k in ("performance", "accessibility", "best-practices", "seo")}
        return httpx.Response(200, json={"lighthouseResult": {"categories": cats, "audits": audits}})
    headers = {
        "strict-transport-security": "max-age=1",
        "x-frame-options": "DENY",
        "x-content-type-options": "nosniff",
        "referrer-policy": "no-referrer",
        "content-security-policy": "default-src 'self'",
    }
    if request.url.scheme == "http":
        return httpx.Response(301, headers={"location": "https://example.com/"})
    return httpx.Response(200, text=GOOD_HTML, headers=headers)
