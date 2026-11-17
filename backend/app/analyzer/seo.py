import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional
from ..safe_url import safe_client
from ..schemas import SEOResult, Check
from .html_utils import images_without_alt, js_rendered_hint

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WebCheckAnalyzer/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de,en;q=0.8",
}

TIMEOUT = 15.0


def _score(checks: list[Check]) -> int:
    if not checks:
        return 0
    scorable = [c for c in checks if c.status != "info"]
    if not scorable:
        return 100
    points = sum(2 if c.status == "pass" else 1 if c.status == "warning" else 0 for c in scorable)
    return round(points / (len(scorable) * 2) * 100)


def _looks_like_html(resp: httpx.Response) -> bool:
    head = resp.text.lstrip()[:200].lower()
    return "text/html" in resp.headers.get("content-type", "").lower() or head.startswith(("<!doctype", "<html"))


def _parse_robots(text: str) -> tuple[bool, list[str]]:
    """Return (blocks_everything, sitemap_urls). Only the '*' user-agent group is judged."""
    blocks_all = False
    sitemaps: list[str] = []
    in_star_group = False
    prev_was_agent = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (x.strip() for x in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            in_star_group = (value == "*") if not prev_was_agent else (in_star_group or value == "*")
            prev_was_agent = True
            continue
        prev_was_agent = False
        if field == "sitemap" and value.lower().startswith(("http://", "https://")):
            sitemaps.append(value)
        elif field == "disallow" and in_star_group and value == "/":
            blocks_all = True
        elif field == "allow" and in_star_group and value == "/":
            blocks_all = False
    return blocks_all, sitemaps


async def _check_robots(base: str) -> tuple[Check, list[str]]:
    try:
        async with safe_client(headers=HEADERS, timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(urljoin(base, "/robots.txt"))
    except Exception:
        return Check(name="robots.txt", status="warning", value="Nicht erreichbar", recommendation="robots.txt konnte nicht geladen werden."), []
    if resp.status_code != 200:
        return Check(name="robots.txt", status="warning", value=f"HTTP {resp.status_code}", recommendation="Erstellen Sie eine robots.txt-Datei."), []
    if _looks_like_html(resp):
        return Check(name="robots.txt", status="warning", value="Keine gültige robots.txt", recommendation="Unter /robots.txt wird eine HTML-Seite ausgeliefert. Legen Sie eine echte robots.txt als Textdatei an."), []
    blocks_all, sitemaps = _parse_robots(resp.text)
    if blocks_all:
        return Check(name="robots.txt", status="fail", value="Sperrt die gesamte Website (Disallow: /)", recommendation="Die robots.txt verbietet allen Suchmaschinen den Zugriff. Entfernen Sie \"Disallow: /\", wenn die Seite gefunden werden soll."), sitemaps
    value = "Vorhanden · verweist auf Sitemap" if sitemaps else "Vorhanden"
    return Check(name="robots.txt", status="pass", value=value), sitemaps


async def _check_sitemap(base: str, robots_sitemaps: list[str]) -> Check:
    default = urljoin(base, "/sitemap.xml")
    candidates = [default] + [u for u in robots_sitemaps if u != default][:3]
    default_status: int | None = None
    reachable = False
    for candidate in candidates:
        try:
            async with safe_client(headers=HEADERS, timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(candidate)
        except Exception:
            continue
        reachable = True
        if candidate == default:
            default_status = resp.status_code
        if resp.status_code != 200:
            continue
        if candidate.endswith(".gz") or "<urlset" in resp.text[:5000] or "<sitemapindex" in resp.text[:5000]:
            value = "Vorhanden" if candidate == default else f"Vorhanden ({candidate[:70]})"
            return Check(name="sitemap.xml", status="pass", value=value)
    if not reachable:
        return Check(name="sitemap.xml", status="warning", value="Nicht erreichbar", recommendation="sitemap.xml konnte nicht geladen werden.")
    if default_status == 200:
        return Check(name="sitemap.xml", status="warning", value="Keine gültige Sitemap", recommendation="Unter /sitemap.xml liegt keine XML-Sitemap. Erstellen Sie eine gültige Sitemap und reichen Sie sie in der Google Search Console ein.")
    return Check(name="sitemap.xml", status="warning", value=f"HTTP {default_status}" if default_status else "Nicht gefunden", recommendation="Erstellen Sie eine XML-Sitemap und reichen Sie sie in der Google Search Console ein.")


async def analyze(url: str) -> SEOResult:
    try:
        async with safe_client(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
            html = resp.text
            final = urlparse(str(resp.url))

        soup = BeautifulSoup(html, "lxml")
        checks: list[Check] = []
        # robots.txt and sitemap.xml live on the host the page finally resolves to (e.g. after example.com -> www.example.com)
        base = f"{final.scheme}://{final.netloc}"

        # --- Title ---
        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else None
        if not title_text:
            checks.append(Check(name="Title-Tag", status="fail", value="Fehlt", recommendation="Fügen Sie einen einzigartigen <title>-Tag (30–60 Zeichen) hinzu."))
        elif len(title_text) < 30:
            checks.append(Check(name="Title-Tag", status="warning", value=f"{len(title_text)} Zeichen", recommendation="Der Titel ist zu kurz (optimal: 30–60 Zeichen)."))
        elif len(title_text) > 60:
            checks.append(Check(name="Title-Tag", status="warning", value=f"{len(title_text)} Zeichen", recommendation="Der Titel ist zu lang und wird in Google abgeschnitten (max. 60 Zeichen)."))
        else:
            checks.append(Check(name="Title-Tag", status="pass", value=f"{len(title_text)} Zeichen"))

        # --- Meta Description ---
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc_text = desc_tag.get("content", "").strip() if desc_tag else None
        if not desc_text:
            checks.append(Check(name="Meta-Description", status="fail", value="Fehlt", recommendation="Fügen Sie eine Meta-Description (120–160 Zeichen) hinzu."))
        elif len(desc_text) < 120:
            checks.append(Check(name="Meta-Description", status="warning", value=f"{len(desc_text)} Zeichen", recommendation="Meta-Description zu kurz (optimal: 120–160 Zeichen)."))
        elif len(desc_text) > 160:
            checks.append(Check(name="Meta-Description", status="warning", value=f"{len(desc_text)} Zeichen", recommendation="Meta-Description zu lang und wird abgeschnitten (max. 160 Zeichen)."))
        else:
            checks.append(Check(name="Meta-Description", status="pass", value=f"{len(desc_text)} Zeichen"))

        # --- H1 ---
        h1_tags = soup.find_all("h1")
        if len(h1_tags) == 0:
            checks.append(Check(name="H1-Überschrift", status="fail", value="Keine H1 gefunden", recommendation="Jede Seite sollte genau eine H1-Überschrift haben."))
        elif len(h1_tags) > 1:
            checks.append(Check(name="H1-Überschrift", status="warning", value=f"{len(h1_tags)} H1-Tags", recommendation="Zu viele H1-Tags. Nutzen Sie nur eine H1 pro Seite."))
        else:
            checks.append(Check(name="H1-Überschrift", status="pass", value=h1_tags[0].get_text(strip=True)[:60]))

        # --- robots.txt & Sitemap ---
        robots_check, robots_sitemaps = await _check_robots(base)
        checks.append(robots_check)
        checks.append(await _check_sitemap(base, robots_sitemaps))

        # --- Canonical ---
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical:
            checks.append(Check(name="Canonical-URL", status="pass", value=canonical.get("href", "")[:80]))
        else:
            checks.append(Check(name="Canonical-URL", status="warning", value="Fehlt", recommendation="Fügen Sie einen <link rel=\"canonical\"> ein, um Duplicate Content zu vermeiden."))

        # --- Open Graph ---
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        og_count = sum(1 for t in [og_title, og_desc, og_image] if t)
        if og_count == 3:
            checks.append(Check(name="Open Graph Tags", status="pass", value="og:title, og:description, og:image vorhanden"))
        elif og_count > 0:
            checks.append(Check(name="Open Graph Tags", status="warning", value=f"{og_count}/3 Tags", recommendation="Ergänzen Sie fehlende Open Graph Tags für bessere Social-Media-Darstellung."))
        else:
            checks.append(Check(name="Open Graph Tags", status="warning", value="Keine OG-Tags", recommendation="Fügen Sie Open Graph Meta-Tags hinzu (og:title, og:description, og:image)."))

        # --- Language ---
        html_tag = soup.find("html")
        lang = html_tag.get("lang", "") if html_tag else ""
        if lang:
            checks.append(Check(name="Sprache (lang-Attribut)", status="pass", value=lang))
        else:
            checks.append(Check(name="Sprache (lang-Attribut)", status="warning", value="Fehlt", recommendation="Setzen Sie das lang-Attribut im <html>-Tag (z.B. lang=\"de\")."))

        # --- Viewport Meta ---
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport:
            checks.append(Check(name="Viewport Meta-Tag", status="pass", value="Vorhanden (Mobile-freundlich)"))
        else:
            checks.append(Check(name="Viewport Meta-Tag", status="fail", value="Fehlt", recommendation="Fügen Sie <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> hinzu."))

        # --- Image Alt Texts ---
        all_imgs = soup.find_all("img")
        missing_alt = images_without_alt(soup)
        if not all_imgs:
            checks.append(Check(name="Bilder mit Alt-Text", status="info", value="Keine Bilder gefunden"))
        elif len(missing_alt) == 0:
            checks.append(Check(name="Bilder mit Alt-Text", status="pass", value=f"Alle {len(all_imgs)} Bilder haben Alt-Text"))
        elif len(missing_alt) / len(all_imgs) > 0.5:
            checks.append(Check(name="Bilder mit Alt-Text", status="fail", value=f"{len(missing_alt)}/{len(all_imgs)} ohne Alt-Text", recommendation="Fügen Sie allen Bildern beschreibende Alt-Texte hinzu."))
        else:
            checks.append(Check(name="Bilder mit Alt-Text", status="warning", value=f"{len(missing_alt)}/{len(all_imgs)} ohne Alt-Text", recommendation="Einige Bilder haben keinen Alt-Text."))

        # --- Structured Data ---
        ld_json = soup.find("script", attrs={"type": "application/ld+json"})
        if ld_json:
            checks.append(Check(name="Strukturierte Daten (JSON-LD)", status="pass", value="Vorhanden"))
        else:
            checks.append(Check(name="Strukturierte Daten (JSON-LD)", status="info", value="Nicht gefunden", recommendation="Fügen Sie JSON-LD strukturierte Daten hinzu, um Rich Snippets in Google zu ermöglichen."))

        js_hint = js_rendered_hint(html)
        if js_hint:
            checks.append(js_hint)

        return SEOResult(
            score=_score(checks),
            title=title_text,
            description=desc_text,
            checks=checks,
        )

    except Exception as e:
        return SEOResult(score=0, checks=[], error=str(e))
