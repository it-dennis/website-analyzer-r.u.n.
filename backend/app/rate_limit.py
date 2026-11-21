import os
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

# In-memory sliding window per client IP. Valid for a single uvicorn worker (see Dockerfile).
PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "30"))

_hits: dict[str, deque[float]] = defaultdict(deque)
_last_cleanup = 0.0


def _client_ip(request: Request) -> str:
    # nginx sets X-Real-IP; direct access falls back to the socket peer.
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "unknown")


def _cleanup(now: float) -> None:
    global _last_cleanup
    if now - _last_cleanup < 300:
        return
    _last_cleanup = now
    for ip in [ip for ip, q in _hits.items() if not q or now - q[-1] > 3600]:
        del _hits[ip]


async def rate_limit(request: Request) -> None:
    if PER_MINUTE <= 0 and PER_HOUR <= 0:
        return
    now = time.monotonic()
    _cleanup(now)
    hits = _hits[_client_ip(request)]
    while hits and now - hits[0] > 3600:
        hits.popleft()

    last_minute = [t for t in hits if now - t <= 60]
    retry_after = 0
    if PER_MINUTE > 0 and len(last_minute) >= PER_MINUTE:
        retry_after = int(60 - (now - last_minute[0])) + 1
    elif PER_HOUR > 0 and len(hits) >= PER_HOUR:
        retry_after = int(3600 - (now - hits[0])) + 1

    if retry_after:
        raise HTTPException(
            status_code=429,
            detail=f"Zu viele Anfragen. Bitte versuche es in {retry_after} Sekunden erneut.",
            headers={"Retry-After": str(retry_after)},
        )
    hits.append(now)
