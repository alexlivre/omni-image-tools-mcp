"""Automatic image pre-processing pipeline for vision tools.

Applies a fixed pipeline to every image passed to a vision tool, before
any analysis or model call:

  1. Resize (Lanczos) if longest side > 1536 px. Keep original size otherwise.
  2. Convert to RGB (strips alpha if present).
  3. Save as JPEG quality 90, progressive, optimize=True.

Processed images are cached in a temp directory keyed by the SHA-256 of
the original file bytes, so repeated calls with the same image skip work.
"""

import hashlib
import io
import logging
import tempfile
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

MAX_LONGEST_SIDE: int = 1536
KEEP_BELOW: int = 768
JPEG_QUALITY: int = 90
TARGET_MIN_KB: int = 300
TARGET_MAX_KB: int = 1024

CACHE_ROOT: Path = Path(tempfile.gettempdir()) / "omni-image-tools" / "preprocessed"


def _cache_path_for(original_path: Path) -> Path:
    """Return the cache file path for a given original image."""
    h = hashlib.sha256(original_path.read_bytes()).hexdigest()
    return CACHE_ROOT / f"{h}.jpg"


def _resize_if_needed(img: Image.Image) -> Image.Image:
    """Resize with Lanczos if longest side > MAX_LONGEST_SIDE."""
    w, h = img.size
    longest = max(w, h)
    if longest <= MAX_LONGEST_SIDE:
        return img
    scale = MAX_LONGEST_SIDE / longest
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(new_size, Image.LANCZOS)


def _to_jpeg_bytes(img: Image.Image) -> bytes:
    """Convert to RGB and encode as JPEG quality 90 progressive + optimize."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return buf.getvalue()


def preprocess_to_bytes(image_path: str | Path) -> bytes:
    """Return the preprocessed image as JPEG bytes, using a content-hash cache."""
    original_path = Path(image_path)
    if not original_path.is_file():
        raise FileNotFoundError(f"Image not found: {original_path}")

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    cache = _cache_path_for(original_path)
    if cache.is_file():
        return cache.read_bytes()

    with Image.open(original_path) as img:
        img.load()
        resized = _resize_if_needed(img)
        data = _to_jpeg_bytes(resized)

    cache.write_bytes(data)
    logger.debug(
        "Preprocessed %s -> %s (%d bytes, longest_side=%d)",
        original_path, cache, len(data), max(resized.size),
    )
    return data
