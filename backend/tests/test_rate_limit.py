import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import rate_limit


def make_request(ip="1.1.1.1", header=True):
    headers = [(b"x-real-ip", ip.encode())] if header else []
    return Request({"type": "http", "headers": headers, "client": ("9.9.9.9", 1234)})


def hit(**kw):
    asyncio.run(rate_limit.rate_limit(make_request(**kw)))


def test_blocks_after_per_minute_limit(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 3)
    for _ in range(3):
        hit()
    with pytest.raises(HTTPException) as exc:
        hit()
    assert exc.value.status_code == 429
    assert int(exc.value.headers["Retry-After"]) >= 1


def test_limit_is_per_ip(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 1)
    hit(ip="1.1.1.1")
    hit(ip="2.2.2.2")
    with pytest.raises(HTTPException):
        hit(ip="1.1.1.1")


def test_hourly_limit(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_HOUR", 2)
    hit()
    hit()
    with pytest.raises(HTTPException) as exc:
        hit()
    assert exc.value.status_code == 429


def test_window_expires(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 1)
    now = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: now[0])
    hit()
    with pytest.raises(HTTPException):
        hit()
    now[0] += 61
    hit()


def test_zero_disables_limits(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 0)
    monkeypatch.setattr(rate_limit, "PER_HOUR", 0)
    for _ in range(50):
        hit()


def test_falls_back_to_socket_peer_without_header(monkeypatch):
    monkeypatch.setattr(rate_limit, "PER_MINUTE", 1)
    hit(header=False)
    with pytest.raises(HTTPException):
        hit(header=False)
    assert "9.9.9.9" in rate_limit._hits
