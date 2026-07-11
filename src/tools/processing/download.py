"""Download image from URL tool for omni-image-tools-mcp."""

from pathlib import Path
from typing import Any

import aiofiles
import httpx
from PIL import Image

from io import BytesIO


async def download_image(url: str) -> dict[str, Any]:
    """Download an image from a URL and save it locally.

    Args:
        url: HTTP/HTTPS URL of the image

    Returns:
        Dict with local path, format, size info
    """
    import uuid

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.read()
    except httpx.TimeoutException:
        return {"success": False, "error": "Download timed out after 30 seconds"}
    except httpx.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e}"}

    if len(content) > 20 * 1024 * 1024:
        return {"success": False, "error": f"Image too large: {len(content)} bytes (max 20MB)"}

    try:
        img = Image.open(BytesIO(content))
        img_format = img.format or "JPEG"
        width, height = img.size
        img.verify()
    except Exception:
        return {"success": False, "error": "URL does not point to a valid image"}

    ext = _guess_extension(img_format)
    filename = f"downloaded_{uuid.uuid4().hex[:8]}{ext}"
    save_dir = Path(__file__).parent.parent.parent.parent / "test_images"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / filename

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    return {
        "success": True,
        "local_path": str(save_path),
        "format": img_format,
        "width": width,
        "height": height,
        "file_size_bytes": len(content),
        "file_size_kb": round(len(content) / 1024, 1),
        "original_url": url,
    }


def _guess_extension(format_name: str) -> str:
    """Guess file extension from PIL format name."""
    mapping = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "GIF": ".gif",
        "BMP": ".bmp",
        "TIFF": ".tiff",
    }
    return mapping.get(format_name.upper(), ".jpg")
