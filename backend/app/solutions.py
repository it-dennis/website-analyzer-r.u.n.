"""Einheitliche Zuordnung: Befund -> was Dennis Rapp IT daran konkret macht.

Wird von der Webseite UND vom PDF genutzt (beide bekommen `findings` aus der API),
damit überall dieselben Aussagen stehen. Hier ist die EINE Stelle zum Anpassen.
Preise stehen bewusst nicht im Code: Aufwand-Stufen + "Preis nach Absprache".
"""
from typing import List
from .schemas import AnalysisResult, Finding, Solution

# Aufwand-Stufen (Stunden nur als grobe Orientierung, kein Preis)
QUICK = "Schnell erledigt (ca. bis 1 Std.)"
MEDIUM = "Überschaubar (ca. 1–4 Std.)"
LARGE = "Größeres Paket (Preis nach Sichtung)"

SEC, VIS, SITE, SPEED = "Sicherheit", "Sichtbarkeit", "Inhalt & Aufbau", "Tempo"

# Name des Checks -> (Bereich, Lösung, Aufwand, Risiko-Gewicht 1-3)
MAP = {
    "HTTPS": (SEC, "HTTPS einrichten und Zertifikat einbinden, inklusive Umleitung aller Adressen.", MEDIUM, 3),
    "HTTP→HTTPS Weiterleitung": (SEC, "Weiterleitung auf HTTPS in der Server-Konfiguration einrichten.", QUICK, 2),
    "SSL-Zertifikat": (SEC, "Zertifikat erneuern bzw. korrekt installieren und automatische Verlängerung einrichten.", QUICK, 3),
    "HSTS (Strict-Transport-Security)": (SEC, "Sicherheits-Header setzen (HSTS), sauber getestet, ohne die Seite zu sperren.", QUICK, 2),
    "X-Frame-Options": (SEC, "Header gegen Clickjacking ergänzen.", QUICK, 1),
    "X-Content-Type-Options": (SEC, "Header gegen MIME-Sniffing ergänzen.", QUICK, 1),
    "Referrer-Policy": (SEC, "Referrer-Policy festlegen, damit keine unnötigen Daten weitergegeben werden.", QUICK, 1),
    "Content-Security-Policy (CSP)": (SEC, "Passende Content-Security-Policy entwerfen und testen (schützt vor eingeschleustem Code).", MEDIUM, 2),
    "Title-Tag": (VIS, "Seitentitel pro Seite so formulieren, dass er in Google zieht.", QUICK, 2),
    "Meta-Description": (VIS, "Beschreibungstexte für die Suchergebnisse schreiben.", QUICK, 2),
    "H1-Überschrift": (VIS, "Überschriftenstruktur korrigieren (eine H1 pro Seite).", QUICK, 2),
    "robots.txt": (VIS, "robots.txt anlegen.", QUICK, 1),
    "sitemap.xml": (VIS, "Sitemap erzeugen und bei Google anmelden.", QUICK, 2),
    "Canonical-URL": (VIS, "Canonical-Angaben ergänzen, damit keine doppelten Inhalte entstehen.", QUICK, 1),
    "Open Graph Tags": (VIS, "Vorschau für WhatsApp, LinkedIn & Co. einrichten (Titel, Text, Bild).", QUICK, 1),
    "Sprache (lang-Attribut)": (SITE, "Seitensprache korrekt auszeichnen.", QUICK, 1),
    "Viewport Meta-Tag": (SITE, "Seite für Smartphones nutzbar machen (Viewport, ggf. responsives Layout).", MEDIUM, 3),
    "Bilder mit Alt-Text": (SITE, "Alternativtexte für Bilder ergänzen (hilft Barrierefreiheit und Suche).", QUICK, 1),
    "Bilder Alt-Texte": (SITE, "Alternativtexte für Bilder ergänzen (hilft Barrierefreiheit und Suche).", QUICK, 1),
    "Strukturierte Daten (JSON-LD)": (VIS, "Strukturierte Daten für Firma und Angebot einbauen (z. B. lokale Suche).", QUICK, 1),
    "Textmenge": (SITE, "Inhalte gemeinsam mit Dir ausbauen, damit die Seite für Besucher und Suche genug bietet.", LARGE, 1),
    "Überschriftenstruktur": (SITE, "Inhalte sauber in Abschnitte gliedern.", QUICK, 1),
    "Interne Verlinkung": (SITE, "Seiten sinnvoll untereinander verlinken.", QUICK, 1),
}

PERF = (SPEED, "Ladezeit verbessern: Bilder optimieren, Caching und Komprimierung einrichten, ggf. auf schnelleres Hosting umziehen.", MEDIUM, 3)


def _finding(area: str, name: str, status: str, value, rec, sol: tuple) -> Finding:
    _, fix, effort, weight = sol
    return Finding(
        area=area, name=name, status=status, value=value, recommendation=rec,
        weight=weight, solution=Solution(fix=fix, effort=effort),
    )


def build_findings(r: AnalysisResult) -> List[Finding]:
    out: List[Finding] = []
    seen = set()  # gleiche Maßnahme nur einmal listen (z. B. Alt-Texte stecken in SEO und Inhalt)
    for group in (r.security.checks, r.seo.checks, r.content.checks):
        for c in group:
            if c.status not in ("fail", "warning"):
                continue
            sol = MAP.get(c.name)
            if not sol or c.name in seen or sol[1] in seen:
                continue
            seen.add(c.name)
            seen.add(sol[1])
            out.append(_finding(sol[0], c.name, c.status, c.value, c.recommendation, sol))
    p = r.performance.score
    if p is not None and p < 90:
        out.append(_finding(SPEED, "Ladezeit mobil", "fail" if p < 50 else "warning",
                            f"Performance-Wert {p}/100", "Die Seite lädt auf dem Smartphone spürbar langsam.", PERF))
    # Wichtigstes zuerst: Fehler vor Warnung, dann Gewicht
    out.sort(key=lambda f: (f.status != "fail", -f.weight))
    return out
