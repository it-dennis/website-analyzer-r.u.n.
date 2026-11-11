import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional
from ..safe_url import safe_client
from ..schemas import SEOResult, Check

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


async def analyze(url: str) -> SEOResult:
    try:
        async with safe_client(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
            html = resp.text

        soup = BeautifulSoup(html, "lxml")
        checks: list[Check] = []
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # --- Title ---
        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else None
        if not title_text:
            checks.append(Check(name="Title-Tag", status="fail", value="Fehlt", recommendation="Füge einen einzigartigen <title>-Tag (30–60 Zeichen) hinzu."))
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
            checks.append(Check(name="Meta-Description", status="fail", value="Fehlt", recommendation="Füge eine Meta-Description (120–160 Zeichen) hinzu."))
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
            checks.append(Check(name="H1-Überschrift", status="warning", value=f"{len(h1_tags)} H1-Tags", recommendation="Zu viele H1-Tags. Nutze nur eine H1 pro Seite."))
        else:
            checks.append(Check(name="H1-Überschrift", status="pass", value=h1_tags[0].get_text(strip=True)[:60]))

        # --- robots.txt ---
        robots_url = urljoin(base, "/robots.txt")
        try:
            async with safe_client(timeout=8.0) as client:
                robots_resp = await client.get(robots_url)
            if robots_resp.status_code == 200:
                checks.append(Check(name="robots.txt", status="pass", value="Vorhanden"))
            else:
                checks.append(Check(name="robots.txt", status="warning", value=f"HTTP {robots_resp.status_code}", recommendation="Erstelle eine robots.txt-Datei."))
        except Exception:
            checks.append(Check(name="robots.txt", status="warning", value="Nicht erreichbar", recommendation="robots.txt konnte nicht geladen werden."))

        # --- Sitemap ---
        sitemap_url = urljoin(base, "/sitemap.xml")
        try:
            async with safe_client(timeout=8.0) as client:
                sitemap_resp = await client.get(sitemap_url)
            if sitemap_resp.status_code == 200:
                checks.append(Check(name="sitemap.xml", status="pass", value="Vorhanden"))
            else:
                checks.append(Check(name="sitemap.xml", status="warning", value=f"HTTP {sitemap_resp.status_code}", recommendation="Erstelle eine XML-Sitemap und reiche sie bei Google Search Console ein."))
        except Exception:
            checks.append(Check(name="sitemap.xml", status="warning", value="Nicht erreichbar", recommendation="sitemap.xml konnte nicht geladen werden."))

        # --- Canonical ---
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical:
            checks.append(Check(name="Canonical-URL", status="pass", value=canonical.get("href", "")[:80]))
        else:
            checks.append(Check(name="Canonical-URL", status="warning", value="Fehlt", recommendation="Füge einen <link rel=\"canonical\"> ein, um Duplicate Content zu vermeiden."))

        # --- Open Graph ---
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        og_count = sum(1 for t in [og_title, og_desc, og_image] if t)
        if og_count == 3:
            checks.append(Check(name="Open Graph Tags", status="pass", value="og:title, og:description, og:image vorhanden"))
        elif og_count > 0:
            checks.append(Check(name="Open Graph Tags", status="warning", value=f"{og_count}/3 Tags", recommendation="Ergänze fehlende Open Graph Tags für bessere Social-Media-Darstellung."))
        else:
            checks.append(Check(name="Open Graph Tags", status="warning", value="Keine OG-Tags", recommendation="Füge Open Graph Meta-Tags hinzu (og:title, og:description, og:image)."))

        # --- Language ---
        html_tag = soup.find("html")
        lang = html_tag.get("lang", "") if html_tag else ""
        if lang:
            checks.append(Check(name="Sprache (lang-Attribut)", status="pass", value=lang))
        else:
            checks.append(Check(name="Sprache (lang-Attribut)", status="warning", value="Fehlt", recommendation="Setze das lang-Attribut im <html>-Tag (z.B. lang=\"de\")."))

        # --- Viewport Meta ---
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport:
            checks.append(Check(name="Viewport Meta-Tag", status="pass", value="Vorhanden (Mobile-freundlich)"))
        else:
            checks.append(Check(name="Viewport Meta-Tag", status="fail", value="Fehlt", recommendation="Füge <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> hinzu."))

        # --- Image Alt Texts ---
        all_imgs = soup.find_all("img")
        missing_alt = [img for img in all_imgs if not img.get("alt")]
        if not all_imgs:
            checks.append(Check(name="Bilder mit Alt-Text", status="info", value="Keine Bilder gefunden"))
        elif len(missing_alt) == 0:
            checks.append(Check(name="Bilder mit Alt-Text", status="pass", value=f"Alle {len(all_imgs)} Bilder haben Alt-Text"))
        elif len(missing_alt) / len(all_imgs) > 0.5:
            checks.append(Check(name="Bilder mit Alt-Text", status="fail", value=f"{len(missing_alt)}/{len(all_imgs)} ohne Alt-Text", recommendation="Füge beschreibende Alt-Texte zu allen Bildern hinzu."))
        else:
            checks.append(Check(name="Bilder mit Alt-Text", status="warning", value=f"{len(missing_alt)}/{len(all_imgs)} ohne Alt-Text", recommendation="Einige Bilder haben keinen Alt-Text."))

        # --- Structured Data ---
        ld_json = soup.find("script", attrs={"type": "application/ld+json"})
        if ld_json:
            checks.append(Check(name="Strukturierte Daten (JSON-LD)", status="pass", value="Vorhanden"))
        else:
            checks.append(Check(name="Strukturierte Daten (JSON-LD)", status="info", value="Nicht gefunden", recommendation="Füge JSON-LD strukturierte Daten hinzu, um Rich Snippets in Google zu ermöglichen."))

        return SEOResult(
            score=_score(checks),
            title=title_text,
            description=desc_text,
            checks=checks,
        )

    except Exception as e:
        return SEOResult(score=0, checks=[], error=str(e))
