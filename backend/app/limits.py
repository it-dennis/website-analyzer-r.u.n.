"""Eigene Rate-Limits für Newsletter-Eintragung und PDF (getrennt vom Scan-Limit in rate_limit.py)."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, limit: int, window_s: int):
        self.limit, self.window = limit, window_s
        self.hits: dict[str, deque] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            raise HTTPException(status_code=429, detail="Zu viele Anfragen. Bitte versuchen Sie es in einigen Minuten erneut.",
                                headers={"Retry-After": str(int(self.window - (now - q[0])) + 1)})
        q.append(now)
        if len(self.hits) > 5000:
            for k in [k for k, v in self.hits.items() if not v or now - v[-1] > self.window]:
                self.hits.pop(k, None)
