import re
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

HSTS_MIN_SECONDS = 15552000  # 180 days
REFERRER_POLICIES = {
    "no-referrer", "no-referrer-when-downgrade", "origin", "origin-when-cross-origin",
    "same-origin", "strict-origin", "strict-origin-when-cross-origin", "unsafe-url",
}


def _short(val: str) -> str:
    return val[:80]


def _csp_directives(csp: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for part in csp.split(";"):
        tokens = part.split()
        if tokens:
            out.setdefault(tokens[0].lower(), [t.lower() for t in tokens[1:]])
    return out


def _evaluate_headers(headers: dict[str, str]) -> list[Check]:
    """Presence and basic sanity of the five security headers. `headers` keys are lowercase."""
    checks: list[Check] = []
    csp = headers.get("content-security-policy", "")
    csp_dirs = _csp_directives(csp) if csp else {}

    # HSTS
    name = "HSTS (Strict-Transport-Security)"
    val = headers.get("strict-transport-security")
    if not val:
        checks.append(Check(name=name, status="warning", value="Fehlt", recommendation="Schützt vor Downgrade-Angriffen. Füge den HSTS-Header hinzu."))
    else:
        m = re.search(r"max-age\s*=\s*\"?(\d+)", val, re.I)
        age = int(m.group(1)) if m else 0
        if age < HSTS_MIN_SECONDS:
            checks.append(Check(name=name, status="warning", value=_short(val), recommendation=f"Die HSTS-Laufzeit ist zu kurz. Empfohlen: max-age von mindestens {HSTS_MIN_SECONDS} Sekunden (besser 31536000)."))
        else:
            checks.append(Check(name=name, status="pass", value=_short(val)))

    # X-Frame-Options (CSP frame-ancestors is the modern equivalent)
    name = "X-Frame-Options"
    val = headers.get("x-frame-options")
    if val and val.strip().upper() in ("DENY", "SAMEORIGIN"):
        checks.append(Check(name=name, status="pass", value=_short(val)))
    elif "frame-ancestors" in csp_dirs:
        checks.append(Check(name=name, status="pass", value="Über CSP frame-ancestors geregelt"))
    elif val:
        checks.append(Check(name=name, status="warning", value=_short(val), recommendation="Ungültiger oder veralteter Wert. Setze X-Frame-Options: DENY oder SAMEORIGIN."))
    else:
        checks.append(Check(name=name, status="warning", value="Fehlt", recommendation="Verhindert Clickjacking-Angriffe. Setze X-Frame-Options: DENY oder SAMEORIGIN."))

    # X-Content-Type-Options
    name = "X-Content-Type-Options"
    val = headers.get("x-content-type-options")
    if val and val.strip().lower() == "nosniff":
        checks.append(Check(name=name, status="pass", value=_short(val)))
    elif val:
        checks.append(Check(name=name, status="warning", value=_short(val), recommendation="Ungültiger Wert. Setze X-Content-Type-Options: nosniff."))
    else:
        checks.append(Check(name=name, status="warning", value="Fehlt", recommendation="Verhindert MIME-Sniffing. Setze X-Content-Type-Options: nosniff."))

    # Referrer-Policy
    name = "Referrer-Policy"
    val = headers.get("referrer-policy")
    if not val:
        checks.append(Check(name=name, status="warning", value="Fehlt", recommendation="Kontrolliert welche Referrer-Informationen gesendet werden."))
    else:
        policies = [p.strip().lower() for p in val.split(",") if p.strip()]
        effective = next((p for p in reversed(policies) if p in REFERRER_POLICIES), None)
        if effective is None:
            checks.append(Check(name=name, status="warning", value=_short(val), recommendation="Unbekannter Wert. Empfohlen: strict-origin-when-cross-origin oder no-referrer."))
        elif effective == "unsafe-url":
            checks.append(Check(name=name, status="warning", value=_short(val), recommendation="unsafe-url gibt die vollständige URL an Dritte weiter. Empfohlen: strict-origin-when-cross-origin."))
        else:
            checks.append(Check(name=name, status="pass", value=_short(val)))

    # Content-Security-Policy
    name = "Content-Security-Policy (CSP)"
    if not csp:
        checks.append(Check(name=name, status="warning", value="Fehlt", recommendation="Schützt vor XSS-Angriffen. Definiere eine CSP-Richtlinie."))
    else:
        script_src = csp_dirs.get("script-src", csp_dirs.get("default-src", []))
        protected = any(t.startswith(("'nonce-", "'sha")) or t == "'strict-dynamic'" for t in script_src)
        weak = "'unsafe-eval'" in script_src or ("'unsafe-inline'" in script_src and not protected)
        if weak:
            checks.append(Check(name=name, status="warning", value=_short(csp), recommendation="Die CSP erlaubt 'unsafe-inline' oder 'unsafe-eval' für Skripte und bietet damit nur eingeschränkten XSS-Schutz."))
        else:
            checks.append(Check(name=name, status="pass", value=_short(csp)))

    return checks


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

        checks.extend(_evaluate_headers(headers))

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
