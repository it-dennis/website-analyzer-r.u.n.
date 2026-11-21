"""PDF-Auswertung (fpdf2). Enthält klickbare Anfrage-Links (mailto + Webseite)."""
from datetime import datetime
from urllib.parse import quote
from fpdf import FPDF
from .schemas import AnalysisResult

NAVY = (30, 46, 55)
BLUE = (28, 84, 156)
INK = (40, 52, 60)
MUTE = (100, 119, 133)
MAIL = "info@dennisrapp.com"
SITE = "https://dennisrapp.com"


def _t(s) -> str:
    """Core-Schriften kennen nur Latin-1: typografische Zeichen ersetzen."""
    s = str(s or "")
    for a, b in {"–": "-", "—": "-", "→": "->", "…": "...", "„": '"', "“": '"', "”": '"', "’": "'", "≥": ">=", "·": "-"}.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


def request_mailto(domain: str, r: AnalysisResult, only=None) -> str:
    lines = [f"- {f.name} ({f.area})" for f in ([only] if only else r.findings[:12])]
    body = (f"Hallo Herr Rapp,\n\nich habe die Auswertung für {domain} erhalten und möchte, "
            f"dass Sie sich die folgenden Punkte ansehen:\n\n" + "\n".join(lines) +
            "\n\nBitte melden Sie sich, damit wir Umfang und Preis besprechen können.\n")
    return f"mailto:{MAIL}?subject={quote('Anfrage zur Website-Auswertung: ' + domain)}&body={quote(body)}"


def request_web(domain: str) -> str:
    return f"{SITE}/?domain={quote(domain)}#anfrage"


class _Pdf(FPDF):
    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTE)
        self.cell(0, 5, _t(f"Dennis Rapp IT-Agency - dennisrapp.com - Seite {self.page_no()}"), align="C")


def build(r: AnalysisResult, domain: str) -> bytes:
    pdf = _Pdf(format="A4")
    pdf.set_auto_page_break(True, margin=20)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()

    # Kopf
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 44, "F")
    pdf.set_xy(18, 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "DENNIS RAPP IT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, _t(f"Website-Auswertung: {domain}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(190, 205, 218)
    pdf.cell(0, 6, _t(f"Erstellt am {datetime.now().strftime('%d.%m.%Y')} - automatische Prüfung der Startseite"))
    pdf.set_y(54)

    # Gesamtwert
    pdf.set_text_color(*BLUE)
    pdf.set_font("Helvetica", "B", 34)
    pdf.cell(38, 16, f"{r.overall_score}")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*INK)
    perf = r.performance.score
    parts = [f"Sicherheit {r.security.score}", f"Sichtbarkeit {r.seo.score}", f"Inhalt {r.content.score}",
             f"Tempo {perf if perf is not None else '-'}"]
    pdf.multi_cell(0, 6, align="L", text=_t("von 100 Punkten gesamt\n" + "   |   ".join(parts)), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    n_fail = sum(1 for f in r.findings if f.status == "fail")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.multi_cell(0, 5.5, align="L", text=_t(
        f"Gefunden wurden {len(r.findings)} Punkte, davon {n_fail} mit hoher Dringlichkeit. "
        "Zu jedem Punkt steht, was ich dafür tun würde. Den Preis besprechen wir gemeinsam, "
        "nachdem ich mir die Seite angesehen habe."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    mailto = request_mailto(domain, r)
    web = request_web(domain)

    # Befunde
    for f in r.findings:
        if pdf.get_y() > 235:
            pdf.add_page()
        high = f.status == "fail"
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(180, 66, 42) if high else pdf.set_text_color(154, 101, 16)
        pdf.cell(0, 5, _t(f"{'DRINGEND' if high else 'VERBESSERN'}  -  {f.area.upper()}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6.5, _t(f.name), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*INK)
        if f.value:
            pdf.multi_cell(0, 5, align="L", text=_t(f"Befund: {f.value}"), new_x="LMARGIN", new_y="NEXT")
        if f.recommendation:
            pdf.multi_cell(0, 5, align="L", text=_t(f.recommendation), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*BLUE)
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 5, align="L", text=_t(f"So löse ich das: {f.solution.fix}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MUTE)
        pdf.cell(0, 5, _t(f"Aufwand: {f.solution.effort}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*BLUE)
        pdf.set_font("Helvetica", "U", 9)
        pdf.cell(0, 5, "Diesen Punkt anfragen", link=request_mailto(domain, r, f), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(220, 228, 234)
        pdf.ln(2)
        pdf.line(18, pdf.get_y(), 192, pdf.get_y())
        pdf.ln(4)

    # Abschluss
    if pdf.get_y() > 220:
        pdf.add_page()
    pdf.set_fill_color(*NAVY)
    y = pdf.get_y() + 2
    pdf.rect(18, y, 174, 36, "F")
    pdf.set_xy(24, y + 5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 6, _t("Soll ich mir das ansehen?"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(24)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _t("Ein Klick genügt - Domain und Befunde sind schon in der Mail."), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(24)
    pdf.set_font("Helvetica", "BU", 11)
    pdf.set_text_color(150, 200, 250)
    pdf.cell(0, 7, _t(f"Anfrage per E-Mail senden ({MAIL})"), link=mailto, new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(24)
    pdf.set_font("Helvetica", "U", 10)
    pdf.cell(0, 6, "Oder über die Webseite anfragen", link=web)

    return bytes(pdf.output())
