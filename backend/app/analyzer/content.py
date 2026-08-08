import httpx
import re
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urljoin
from ..schemas import ContentResult, Check

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WebCheckAnalyzer/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}
TIMEOUT = 15.0


def _score(checks: list[Check]) -> int:
    scorable = [c for c in checks if c.status != "info"]
    if not scorable:
        return 100
    points = sum(2 if c.status == "pass" else 1 if c.status == "warning" else 0 for c in scorable)
    return round(points / (len(scorable) * 2) * 100)


def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


async def analyze(url: str) -> ContentResult:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)

        soup = BeautifulSoup(resp.text, "lxml")
        parsed = urlparse(url)
        domain = parsed.netloc

        text = _extract_text(BeautifulSoup(resp.text, "lxml"))
        words = text.split()
        word_count = len(words)
        reading_time = round(word_count / 200, 1)

        # Links
        all_links = soup.find_all("a", href=True)
        internal, external = 0, 0
        for a in all_links:
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            abs_href = urljoin(url, href)
            link_domain = urlparse(abs_href).netloc
            if link_domain == domain or link_domain == "":
                internal += 1
            else:
                external += 1

        # Images
        all_imgs = soup.find_all("img")
        missing_alt = [img for img in all_imgs if not img.get("alt")]

        # Headings
        h1 = soup.find_all("h1")
        h2 = soup.find_all("h2")
        h3 = soup.find_all("h3")

        checks: list[Check] = []

        # Word count
        if word_count < 100:
            checks.append(Check(name="Textmenge", status="fail", value=f"{word_count} Wörter", recommendation="Zu wenig Inhalt. Mindestens 300 Wörter empfohlen für SEO."))
        elif word_count < 300:
            checks.append(Check(name="Textmenge", status="warning", value=f"{word_count} Wörter", recommendation="Mehr Text empfohlen (≥300 Wörter) für bessere Sichtbarkeit."))
        else:
            checks.append(Check(name="Textmenge", status="pass", value=f"{word_count} Wörter · ca. {reading_time} Min. Lesezeit"))

        # Heading structure
        if h2:
            checks.append(Check(name="Überschriftenstruktur", status="pass", value=f"H1: {len(h1)} · H2: {len(h2)} · H3: {len(h3)}"))
        else:
            checks.append(Check(name="Überschriftenstruktur", status="warning", value=f"H1: {len(h1)} · keine H2", recommendation="Strukturiere Inhalte mit H2 und H3 Überschriften."))

        # Images & Alt
        if all_imgs:
            if not missing_alt:
                checks.append(Check(name="Bilder Alt-Texte", status="pass", value=f"{len(all_imgs)} Bilder, alle mit Alt-Text"))
            else:
                pct = round(len(missing_alt) / len(all_imgs) * 100)
                checks.append(Check(name="Bilder Alt-Texte", status="warning" if pct < 50 else "fail", value=f"{len(missing_alt)}/{len(all_imgs)} ohne Alt-Text ({pct}%)", recommendation="Alle Bilder sollten beschreibende Alt-Texte haben."))
        else:
            checks.append(Check(name="Bilder Alt-Texte", status="info", value="Keine Bilder gefunden"))

        # Links
        checks.append(Check(name="Interne Verlinkung", status="pass" if internal >= 3 else "warning", value=f"{internal} interne Links", recommendation=None if internal >= 3 else "Mehr interne Verlinkungen verbessern die Navigation und SEO."))
        checks.append(Check(name="Externe Links", status="info", value=f"{external} externe Links"))

        return ContentResult(
            score=_score(checks),
            word_count=word_count,
            reading_time_minutes=reading_time,
            internal_links=internal,
            external_links=external,
            total_images=len(all_imgs),
            images_missing_alt=len(missing_alt),
            checks=checks,
        )

    except Exception as e:
        return ContentResult(score=0, checks=[], error=str(e))
