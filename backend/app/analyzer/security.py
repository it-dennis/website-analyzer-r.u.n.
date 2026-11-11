import httpx
import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Optional
from ..safe_url import safe_client, assert_safe_host
from ..schemas import SecurityResult, Check

TIMEOUT = 15.0


def _score(checks: list[Check]) -> int:
    scorable = [c for c in checks if c.status != "info"]
    if not scorable:
        return 100
    points = sum(2 if c.status == "pass" else 1 if c.status == "warning" else 0 for c in scorable)
    return round(points / (len(scorable) * 2) * 100)


def _get_ssl_info(hostname: str) -> dict:
    try:
        assert_safe_host(hostname, 443)
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as raw_sock:
            with ctx.wrap_socket(raw_sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        expiry_str = cert.get("notAfter", "")
        expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days_left = (expiry - datetime.now(timezone.utc)).days
        issuer_raw = cert.get("issuer", ())
        issuer_dict = {k: v for rdn in issuer_raw for k, v in rdn}
        issuer = issuer_dict.get("organizationName", "Unbekannt")
        return {"valid": True, "days_left": days_left, "issuer": issuer}
    except ssl.SSLCertVerificationError:
        return {"valid": False, "days_left": None, "issuer": None, "error": "Zertifikat ungültig"}
    except Exception as e:
        return {"valid": None, "days_left": None, "issuer": None, "error": str(e)}


async def analyze(url: str) -> SecurityResult:
    try:
        parsed = urlparse(url)
        is_https = parsed.scheme == "https"
        hostname = parsed.hostname or ""

        checks: list[Check] = []

        # --- HTTPS ---
        if is_https:
            checks.append(Check(name="HTTPS", status="pass", value="Aktiv"))
        else:
            checks.append(Check(name="HTTPS", status="fail", value="Nicht aktiv", recommendation="Aktiviere HTTPS mit einem SSL-Zertifikat (z.B. kostenlos über Let's Encrypt)."))

        # --- HTTP → HTTPS Redirect ---
        if is_https:
            http_url = url.replace("https://", "http://", 1)
            try:
                async with safe_client(follow_redirects=False, timeout=8.0) as client:
                    redir_resp = await client.get(http_url)
                location = redir_resp.headers.get("location", "")
                if redir_resp.status_code in (301, 302, 307, 308) and "https" in location.lower():
                    checks.append(Check(name="HTTP→HTTPS Weiterleitung", status="pass", value=f"HTTP {redir_resp.status_code}"))
                else:
                    checks.append(Check(name="HTTP→HTTPS Weiterleitung", status="warning", value="Keine automatische Weiterleitung", recommendation="Leite alle HTTP-Anfragen auf HTTPS weiter."))
            except Exception:
                checks.append(Check(name="HTTP→HTTPS Weiterleitung", status="info", value="Konnte nicht geprüft werden"))

        # --- SSL Certificate ---
        ssl_valid = None
        ssl_days = None
        ssl_issuer = None

        if is_https and hostname:
            ssl_info = _get_ssl_info(hostname)
            ssl_valid = ssl_info.get("valid")
            ssl_days = ssl_info.get("days_left")
            ssl_issuer = ssl_info.get("issuer")

            if ssl_valid is True:
                if ssl_days is not None and ssl_days < 14:
                    checks.append(Check(name="SSL-Zertifikat", status="fail", value=f"Läuft in {ssl_days} Tagen ab!", recommendation="Erneuere das SSL-Zertifikat sofort."))
                elif ssl_days is not None and ssl_days < 30:
                    checks.append(Check(name="SSL-Zertifikat", status="warning", value=f"Läuft in {ssl_days} Tagen ab", recommendation="Plane die Zertifikatserneuerung."))
                else:
                    checks.append(Check(name="SSL-Zertifikat", status="pass", value=f"Gültig · {ssl_days} Tage verbleibend · {ssl_issuer}"))
            elif ssl_valid is False:
                checks.append(Check(name="SSL-Zertifikat", status="fail", value=ssl_info.get("error", "Ungültig"), recommendation="Installiere ein gültiges SSL-Zertifikat."))

        # --- Security Headers ---
        async with safe_client(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
        headers = {k.lower(): v for k, v in resp.headers.items()}

        header_checks = [
            ("strict-transport-security", "HSTS (Strict-Transport-Security)", "Schützt vor Downgrade-Angriffen. Füge den HSTS-Header hinzu."),
            ("x-frame-options", "X-Frame-Options", "Verhindert Clickjacking-Angriffe. Setze X-Frame-Options: DENY oder SAMEORIGIN."),
            ("x-content-type-options", "X-Content-Type-Options", "Verhindert MIME-Sniffing. Setze X-Content-Type-Options: nosniff."),
            ("referrer-policy", "Referrer-Policy", "Kontrolliert welche Referrer-Informationen gesendet werden."),
            ("content-security-policy", "Content-Security-Policy (CSP)", "Schützt vor XSS-Angriffen. Definiere eine CSP-Richtlinie."),
        ]

        for header_key, label, recommendation in header_checks:
            val = headers.get(header_key)
            if val:
                checks.append(Check(name=label, status="pass", value=val[:80] if len(val) > 80 else val))
            else:
                checks.append(Check(name=label, status="warning", value="Fehlt", recommendation=recommendation))

        return SecurityResult(
            score=_score(checks),
            is_https=is_https,
            ssl_valid=ssl_valid,
            ssl_expiry_days=ssl_days,
            ssl_issuer=ssl_issuer,
            checks=checks,
        )

    except Exception as e:
        return SecurityResult(score=0, checks=[], error=str(e))
