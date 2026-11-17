import re

from bs4 import BeautifulSoup, Comment

from ..schemas import Check

_SPA_ROOT_ID = re.compile(r"^(root|app|__next|__nuxt|svelte)$")


def visible_text(soup: BeautifulSoup) -> str:
    """Visible body text. Mutates the soup, so pass a throwaway copy."""
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    return re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()


def images_without_alt(soup: BeautifulSoup) -> list:
    """Images lacking an alt attribute. An empty alt="" marks a decorative image and is valid."""
    return [img for img in soup.find_all("img") if img.get("alt") is None]


def js_rendered_hint(html: str) -> Check | None:
    """Info check if the delivered HTML is nearly empty and looks like a client-side rendered app."""
    soup = BeautifulSoup(html, "lxml")
    noscript_needs_js = any("javascript" in n.get_text().lower() for n in soup.find_all("noscript"))
    spa_root = soup.find(id=_SPA_ROOT_ID) is not None
    many_scripts = len(soup.find_all("script", src=True)) >= 3
    if not (spa_root or noscript_needs_js or many_scripts):
        return None
    if len(visible_text(soup).split()) >= 50:
        return None
    return Check(
        name="JavaScript-Inhalte",
        status="info",
        value="Seite lädt Inhalte vermutlich per JavaScript",
        recommendation=(
            "R.U.N. liest nur das ausgelieferte HTML, nicht den per JavaScript nachgeladenen Inhalt. "
            "Die Ergebnisse zu SEO und Content können deshalb unvollständig sein. "
            "Die Performance-Messung von Google rendert die Seite dagegen vollständig."
        ),
    )
