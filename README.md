# R.U.N. – Rapid URL Navigator

Website-Checker: URL eingeben, in Sekunden ein Bericht zu SEO, Performance, Sicherheit und Content. Export als PDF oder Markdown.

- **Backend:** FastAPI (Python 3.11), `httpx`, `BeautifulSoup`
- **Frontend:** React 18, Vite, Tailwind, `@react-pdf/renderer`
- **Deployment:** Docker Compose (nginx liefert das Frontend aus und leitet `/api/` an das Backend weiter)

## Was geprüft wird

| Bereich | Gewicht | Prüfungen |
|---|---|---|
| SEO | 35 % | Title, Meta-Description, H1, `robots.txt`, `sitemap.xml`, Canonical, Open Graph, `lang`, Viewport, Alt-Texte, JSON-LD |
| Performance | 35 % | Google PageSpeed (mobil): Scores sowie FCP, LCP, TBT, CLS, Speed Index |
| Sicherheit | 20 % | HTTPS, HTTP→HTTPS-Weiterleitung, SSL-Zertifikat (Gültigkeit, Ablauf), HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, CSP |
| Content | 10 % | Textmenge, Überschriftenstruktur, Alt-Texte, interne und externe Links |

Jeder Check ergibt `pass` (2 Punkte), `warning` (1) oder `fail` (0); `info` zählt nicht. Der Bereichsscore ist der Punkteanteil in Prozent, der Gesamtscore die gewichtete Summe. Ist keine Performance-Messung verfügbar, geht dafür 50 in den Gesamtscore ein.

## Lokal entwickeln

Voraussetzungen: Python 3.11+, Node 20+.

```bash
# Backend (Port 8000)
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (Port 5173, proxyt /api an localhost:8000)
cd frontend
npm install
npm run dev
```

Dann `http://localhost:5173` öffnen. Die API-Doku liegt unter `http://localhost:8000/docs`.

## Konfiguration

**Backend** (`backend/.env`, Vorlage: `backend/.env.example`)

| Variable | Bedeutung | Standard |
|---|---|---|
| `PAGESPEED_API_KEY` | Google-PageSpeed-API-Key. Ohne Key sind die Anfragen stark limitiert (schnell HTTP 429). | leer |
| `ALLOWED_ORIGINS` | Kommagetrennte Liste zusätzlicher CORS-Origins, z. B. `https://example.com` | leer |
| `RATE_LIMIT_PER_MINUTE` | Scans pro IP und Minute (`0` = aus) | `5` |
| `RATE_LIMIT_PER_HOUR` | Scans pro IP und Stunde (`0` = aus) | `30` |

**Frontend** (Build-Zeit)

| Variable | Bedeutung |
|---|---|
| `VITE_BOOKING_URL` | URL der Buchungsseite. Ist sie gesetzt, erscheint nach jedem Scan ein „Audit buchen“-Banner. Die gescannte URL wird als `?url=` übergeben. Ohne Wert bleibt der Banner ausgeblendet. |

Mit Docker Compose liest Compose `VITE_BOOKING_URL` aus der Shell oder aus einer `.env` im Projektroot (nicht aus `frontend/.env.example`) und reicht sie als Build-Argument weiter.

Die Startseite akzeptiert `?url=example.com` und füllt damit das Eingabefeld vor.

## Deployment

```bash
cp backend/.env.example backend/.env    # und ausfüllen
echo "VITE_BOOKING_URL=https://deine-domain.de/webseiten-check.html" > .env   # optional
docker compose -f docker-compose.prod.yml up -d --build
```

`deploy.sh` macht auf dem Server `git pull`, baut neu und räumt alte Images auf.

- `docker-compose.yml` veröffentlicht zusätzlich Port 8000 des Backends (für die Entwicklung). `docker-compose.prod.yml` tut das nicht; nur nginx auf Port 80 ist erreichbar.
- nginx spricht nur HTTP. Für HTTPS einen Reverse Proxy oder Load Balancer davorschalten (z. B. Caddy, Traefik, Cloudflare).
- Das Rate-Limit nutzt den Header `X-Real-IP`, den nginx aus der Client-Adresse setzt. Steht vor nginx ein weiterer Proxy, muss dieser die echte Client-IP weitergeben, sonst teilen sich alle Nutzer ein Limit.
- Die Rate-Limit-Zähler liegen im Arbeitsspeicher. Das ist für einen einzelnen uvicorn-Prozess (wie im Dockerfile) gedacht; bei mehreren Workern oder Replikas wäre ein gemeinsamer Speicher wie Redis nötig.

## Sicherheit

Das Backend ruft die eingegebenen URLs selbst ab. Deshalb gilt:

- **SSRF-Schutz:** Adressen, die auf interne oder reservierte IPs zeigen (Loopback, private Netze, Link-local/Cloud-Metadaten), werden abgelehnt. Das gilt auch für jede Weiterleitung. Erlaubt sind nur `http`/`https`, nur Port 80 und 443, und keine URLs mit Zugangsdaten. Code: `backend/app/safe_url.py`.
- **Rate-Limiting:** pro IP, siehe Konfiguration. Code: `backend/app/rate_limit.py`.
- Bekannte Restlücke: DNS-Rebinding (der Hostname wird zwischen Prüfung und Verbindungsaufbau erneut aufgelöst).

## API

`POST /api/analyze` mit `{"url": "example.com"}` liefert den Gesamtbericht (`overall_score`, `seo`, `performance`, `security`, `content`, `http_status`, …).

| Status | Bedeutung |
|---|---|
| 200 | Analyse durchgeführt. Antwortet die Seite selbst mit HTTP ≥ 400, steht das in `http_status`, und das Frontend zeigt eine Warnung. |
| 400 | URL abgelehnt: ungültig, Domain nicht gefunden oder interne Adresse |
| 429 | Rate-Limit überschritten (Header `Retry-After`) |
| 502 | Seite nicht erreichbar: Timeout, Verbindung abgelehnt, ungültiges SSL-Zertifikat oder Weiterleitungsschleife |

`GET /api/health` gibt `{"status": "ok"}` zurück.

## Projektstruktur

```
backend/app/
  main.py            FastAPI-App, CORS
  routes.py          /api/analyze, /api/health, Erreichbarkeitsprüfung
  safe_url.py        SSRF-Schutz
  rate_limit.py      Rate-Limiting
  schemas.py         Pydantic-Modelle
  analyzer/          seo.py, performance.py, security.py, content.py
frontend/src/
  App.tsx, api.ts, types.ts
  components/        Eingabe, Ergebnis-Karten, Export, pdf/ReportPDF.tsx
```

`Website-Checker_von_geplanter_Webseite/` enthält die zugehörige Marketing-Seite (statisches HTML) und ist nicht Teil der App.
