"""Token bucket rate limiter for provider LLM requests.

Opt-in via ``OMNI_RATE_LIMIT_PER_MIN`` (0 = disabled). Tokens are
keyed by ``(provider, model)``; each bucket starts full with
``per_minute`` tokens and refills one token every ``60 / per_minute``
seconds. An acquire blocks until a token is available.
"""

import asyncio
import os


class RateLimiter:
    def __init__(self, per_minute: int | None = None):
        raw = (
            per_minute if per_minute is not None else int(os.getenv("OMNI_RATE_LIMIT_PER_MIN", "0"))
        )
        self._per_minute = max(0, raw)
        self._interval = 60.0 / self._per_minute if self._per_minute else 0.0
        self._tokens: dict[tuple[str, str], float] = {}
        self._last_refill: dict[tuple[str, str], float] = {}

    def _enabled(self) -> bool:
        return self._interval > 0

    async def acquire(self, provider: str, model: str) -> None:
        if not self._enabled():
            return
        key = (provider, model)
        now = asyncio.get_event_loop().time()
        tokens = self._tokens.get(key, float(self._per_minute))
        refilled = (now - self._last_refill.get(key, now)) / self._interval
        tokens = min(float(self._per_minute), tokens + refilled)
        if tokens >= 1.0:
            self._tokens[key] = tokens - 1.0
            self._last_refill[key] = now
            return
        await asyncio.sleep((1.0 - tokens) * self._interval)
        now = asyncio.get_event_loop().time()
        self._tokens[key] = 0.0
        self._last_refill[key] = now


RATE_LIMITER = RateLimiter()
