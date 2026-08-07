"""Security helpers for omni-image-tools-mcp.

Centralizes SSRF protection, path resolution, and numeric clamping reused
across tool handlers. Fail-closed by design: anything we cannot resolve or
validate must be rejected rather than allowed.
"""

import ipaddress
import logging
import socket
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

ALLOWED_URL_SCHEMES = {"http", "https"}

MAX_DOWNLOAD_SIZE: int = 20 * 1024 * 1024
MAX_IMAGE_BYTES: int = 20 * 1024 * 1024
MIN_CROP_DIM: int = 5
MAX_BBOX_FRACTION: float = 0.95


def is_private_ip(ip_str: str) -> bool:
    """Return True if the IP is private/reserved/loopback/link-local/multicast.

    Fail-closed: an unparseable value is treated as private (blocked).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast


def _resolved_ips(hostname: str) -> set[str]:
    """Return the resolved IP strings for a hostname (empty on DNS failure).

    Fail-closed: callers treat an empty set as a resolution failure.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except (socket.gaierror, OSError):
        return set()
    return {str(ai[4][0]) for ai in infos}


def is_safe_url(url: str) -> bool:
    """Return True if a URL is safe to fetch (public target, http(s) only).

    Blocks private/loopback/link-local/reserved/multicast IPs and non-http(s)
    schemes. Fail-closed: DNS resolution errors are blocked.
    """
    if not url or not isinstance(url, str):
        return False

    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        return False
    if not parsed.hostname:
        return False

    ips = _resolved_ips(parsed.hostname)
    if not ips:
        return False
    for ip in ips:
        if is_private_ip(ip):
            return False
    return True


def resolve_safe_path(
    image_path: str | Path,
    allowed_roots: list[Path] | None = None,
) -> Path:
    """Resolve an image path, following symlinks, enforcing an optional sandbox.

    Args:
        image_path: File path as supplied by the caller.
        allowed_roots: Optional list of directories the file must resolve under.
            When None (default), paths are permissive but symlinks are still
            resolved so callers see the real target.

    Raises:
        FileNotFoundError: if the resolved path does not exist.
        ValueError: if a sandbox is configured and the path escapes it.
    """
    resolved = Path(image_path).resolve()

    if not resolved.exists():
        raise FileNotFoundError(f"Image not found: {resolved}")

    if allowed_roots:
        roots = [Path(r).resolve() for r in allowed_roots]
        inside = any(resolved == r or r in resolved.parents for r in roots)
        if not inside:
            raise ValueError(f"Resolved path {resolved} is outside the allowed directories")

    return resolved


def clamp(value: int | float, lo: int | float, hi: int | float) -> int | float:
    """Clamp a numeric value to the inclusive range [lo, hi]."""
    return max(lo, min(value, hi))


__all__ = [
    "ALLOWED_URL_SCHEMES",
    "MAX_DOWNLOAD_SIZE",
    "MAX_IMAGE_BYTES",
    "MIN_CROP_DIM",
    "MAX_BBOX_FRACTION",
    "clamp",
    "is_private_ip",
    "is_safe_url",
    "resolve_safe_path",
]
