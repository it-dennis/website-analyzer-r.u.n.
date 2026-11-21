"""Newsletter-Eintragungen als CSV (öffnet in Excel/LibreOffice), nur auf dem Server, nie öffentlich ausgeliefert.

Spalten: Zeitpunkt (UTC), E-Mail, geprüfte Domain, Einwilligungstext-Version, Status.
Status bleibt "unbestaetigt", bis ein Double-Opt-in-Versand eingerichtet ist.
"""
import csv
import os
import re
import threading
from datetime import datetime, timezone

DATA_DIR = os.getenv("DATA_DIR", "/data")
FILE = os.path.join(DATA_DIR, "newsletter.csv")
CONSENT_VERSION = "2026-11-21-v1"
HEADER = ["zeitpunkt_utc", "email", "domain", "einwilligung_version", "status"]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")
_lock = threading.Lock()


def valid_email(e: str) -> bool:
    return len(e) <= 254 and bool(EMAIL_RE.match(e))


def _safe(cell: str) -> str:
    # CSV-Injection verhindern: Zellen, die mit = + - @ beginnen, würden in Excel als Formel laufen
    cell = cell.replace("\r", " ").replace("\n", " ")
    return "'" + cell if cell[:1] in ("=", "+", "-", "@", "\t") else cell


def add(email: str, domain: str) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with _lock:
        new = not os.path.exists(FILE)
        with open(FILE, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            if new:
                w.writerow(HEADER)
            w.writerow([
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                _safe(email.lower()), _safe(domain[:253]), CONSENT_VERSION, "unbestaetigt",
            ])


def contains(email: str) -> bool:
    if not os.path.exists(FILE):
        return False
    email = email.lower()
    with _lock, open(FILE, newline="", encoding="utf-8-sig") as f:
        return any(len(r) > 1 and r[1].lstrip("'") == email for r in csv.reader(f, delimiter=";"))
