import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

import httpx

ALLOWED_PORTS = {80, 443}


class UnsafeURLError(ValueError):
    pass


def _check_ip(ip: str) -> None:
    addr = ipaddress.ip_address(ip.split("%")[0])
    # IPv4-mapped IPv6 (::ffff:10.0.0.1) must be judged by its IPv4 part
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    if not addr.is_global or addr.is_multicast:
        raise UnsafeURLError("Diese Adresse darf nicht analysiert werden (interne oder reservierte IP).")


def _check_url_parts(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError("Nur http- und https-URLs werden unterstützt.")
    if not parsed.hostname:
        raise UnsafeURLError("Ungültige URL.")
    if parsed.username or parsed.password:
        raise UnsafeURLError("URLs mit Zugangsdaten sind nicht erlaubt.")
    try:
        port = parsed.port
    except ValueError:
        raise UnsafeURLError("Ungültiger Port.")
    if port is not None and port not in ALLOWED_PORTS:
        raise UnsafeURLError("Nur die Ports 80 und 443 sind erlaubt.")
    return parsed.hostname


def assert_safe_host(hostname: str, port: int = 443) -> None:
    """Resolve hostname and reject it if any address is not publicly routable."""
    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise UnsafeURLError("Die Domain konnte nicht gefunden werden. Bitte prüfe die Schreibweise der URL.")
    for info in infos:
        _check_ip(info[4][0])


def assert_safe_url(url: str) -> None:
    hostname = _check_url_parts(url)
    assert_safe_host(hostname)


async def _validate_request(request: httpx.Request) -> None:
    # Runs for every outgoing request, including each redirect hop.
    hostname = _check_url_parts(str(request.url))
    port = request.url.port or (443 if request.url.scheme == "https" else 80)
    await asyncio.get_running_loop().run_in_executor(None, assert_safe_host, hostname, port)


def safe_client(**kwargs) -> httpx.AsyncClient:
    """AsyncClient that refuses requests to internal addresses, also across redirects."""
    hooks = kwargs.pop("event_hooks", {})
    hooks.setdefault("request", []).insert(0, _validate_request)
    return httpx.AsyncClient(event_hooks=hooks, **kwargs)
