"""Brevo-Anbindung: trägt Eintragungen mit Double-Opt-in in die Newsletter-Liste ein.

Ohne BREVO_API_KEY passiert nichts (nur die CSV wird geschrieben). Fehler bei Brevo
dürfen die Auswertung nicht blockieren, deshalb wird nur geloggt.
"""
import logging
import os

import httpx

log = logging.getLogger("run.brevo")
URL = "https://api.brevo.com/v3/contacts/doubleOptinConfirmation"


def enabled() -> bool:
    return bool(os.getenv("BREVO_API_KEY"))


async def double_optin(email: str) -> bool:
    key = os.getenv("BREVO_API_KEY")
    if not key:
        return False
    body = {
        "email": email,
        "includeListIds": [int(os.getenv("BREVO_LIST_ID", "2"))],
        "templateId": int(os.getenv("BREVO_DOI_TEMPLATE_ID", "1")),
        "redirectionUrl": os.getenv("BREVO_REDIRECT_URL", "https://dennisrapp.com/#check"),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(URL, json=body, headers={"api-key": key, "accept": "application/json"})
        if r.status_code >= 300:
            log.warning("Brevo antwortete %s: %s", r.status_code, r.text[:200])
            return False
        return True
    except httpx.HTTPError as e:
        log.warning("Brevo nicht erreichbar: %s", type(e).__name__)
        return False
