"""In-memory result cache for vision tools.

Opt-in via ``OMNI_VISION_CACHE`` ("1"/"true"/"yes"). Disabled by default.
Keys are ``sha256(tool|image_sha256|prompt|model)`` and entries expire
after ``TTL_SECONDS`` (1h). The cache state is process-local.
"""

import hashlib
import os
import time

_CACHE: dict[str, tuple[float, str]] = {}
TTL_SECONDS: int = 3600


def _is_cache_enabled() -> bool:
    return os.getenv("OMNI_VISION_CACHE", "0").lower() in ("1", "true", "yes")


def __getattr__(name: str) -> bool:
    if name == "_CACHE_ENABLED":
        return _is_cache_enabled()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def make_key(tool: str, image_sha256: str, prompt: str, model: str) -> str:
    """Build a stable cache key from the request parameters."""
    raw = f"{tool}|{image_sha256}|{prompt}|{model}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cached(key: str) -> str | None:
    """Return the cached value for ``key``, or None when disabled/missing/expired."""
    if not _is_cache_enabled():
        return None
    entry = _CACHE.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.monotonic() - ts > TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def cache_result(key: str, value: str) -> None:
    """Store ``value`` under ``key`` when the cache is enabled."""
    if _is_cache_enabled():
        _CACHE[key] = (time.monotonic(), value)
