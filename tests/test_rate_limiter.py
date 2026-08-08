import asyncio

import pytest

from src.utils.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_bucket_allows_rate(monkeypatch):
    monkeypatch.setenv("OMNI_RATE_LIMIT_PER_MIN", "2")
    limiter = RateLimiter()
    t0 = asyncio.get_event_loop().time()
    await limiter.acquire("ollama", "m")
    await limiter.acquire("ollama", "m")
    elapsed = asyncio.get_event_loop().time() - t0
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_bucket_throttles_third(monkeypatch):
    monkeypatch.setenv("OMNI_RATE_LIMIT_PER_MIN", "2")
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    limiter = RateLimiter()
    await limiter.acquire("ollama", "m")
    await limiter.acquire("ollama", "m")
    await limiter.acquire("ollama", "m")
    assert len(sleeps) == 1
    assert sleeps[0] >= 20.0
