import asyncio
import socket

import httpx
import pytest

from app.safe_url import UnsafeURLError, assert_safe_url, safe_client


@pytest.mark.parametrize("ip", [
    "127.0.0.1", "10.0.0.1", "172.16.5.4", "192.168.1.1", "169.254.169.254",
    "0.0.0.0", "::1", "fe80::1", "fc00::1", "::ffff:127.0.0.1", "224.0.0.1",
])
def test_non_public_ips_are_rejected(dns, ip):
    dns["target.test"] = ip
    with pytest.raises(UnsafeURLError):
        assert_safe_url("https://target.test")


def test_public_ip_is_allowed(dns):
    assert_safe_url("https://example.com")
    assert_safe_url("http://example.com:80/path")
    assert_safe_url("https://example.com:443")


def test_any_private_address_among_several_rejects(monkeypatch):
    def mixed(host, port, *a, **k):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", port)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", mixed)
    with pytest.raises(UnsafeURLError):
        assert_safe_url("https://mixed.test")


@pytest.mark.parametrize("url", [
    "ftp://example.com",
    "file:///etc/passwd",
    "https://user:pw@example.com",
    "https://example.com:22",
    "http://example.com:8000",
    "https://",
])
def test_invalid_urls_are_rejected(dns, url):
    with pytest.raises(UnsafeURLError):
        assert_safe_url(url)


def test_unresolvable_host_is_rejected(dns):
    dns["gone.test"] = None
    with pytest.raises(UnsafeURLError, match="Domain"):
        assert_safe_url("https://gone.test")


def test_redirect_to_internal_address_is_blocked(mock_http, dns):
    dns["evil.test"] = "169.254.169.254"

    def handler(request):
        if request.url.host == "example.com":
            return httpx.Response(302, headers={"location": "http://evil.test/secret"})
        return httpx.Response(200, text="SECRET")

    mock_http(handler)

    async def run():
        async with safe_client(follow_redirects=True) as client:
            await client.get("https://example.com")

    with pytest.raises(UnsafeURLError):
        asyncio.run(run())


def test_direct_request_to_internal_address_is_blocked(mock_http, dns):
    dns["internal.test"] = "10.1.2.3"
    mock_http(lambda r: httpx.Response(200, text="SECRET"))

    async def run():
        async with safe_client() as client:
            await client.get("http://internal.test")

    with pytest.raises(UnsafeURLError):
        asyncio.run(run())


def test_public_request_passes(mock_http):
    mock_http(lambda r: httpx.Response(200, text="hello"))

    async def run():
        async with safe_client() as client:
            return (await client.get("https://example.com")).text

    assert asyncio.run(run()) == "hello"
