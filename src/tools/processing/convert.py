"""Convert image format tool for omni-image-tools-mcp."""

from io import BytesIO
from typing import Any

from PIL import Image

_FORMAT_MAP = {
    "JPEG": "JPEG",
    "JPG": "JPEG",
    "PNG": "PNG",
    "WEBP": "WEBP",
    "BMP": "BMP",
    "GIF": "GIF",
}


async def convert_image_format(
    image_path: str,
    output_format: str,
    quality: int = 85,
) -> dict[str, Any]:
    """Convert an image from one format to another.

    Args:
        image_path: Path to the image file
        output_format: Target format (JPEG, PNG, WEBP, BMP, GIF)
        quality: Quality (1-100, for JPEG/WebP)

    Returns:
        Dict with converted image data and info
    """
    target_format = _FORMAT_MAP.get(output_format.upper())
    if not target_format:
        return {
            "success": False,
            "error": f"Unsupported format: {output_format}. Supported: JPEG, PNG, WEBP, BMP, GIF",
        }

    with Image.open(image_path) as img:
        work: Image.Image = img
        if target_format == "JPEG" and img.mode == "RGBA":
            work = img.convert("RGB")
        elif target_format not in ("RGB", "RGBA") and img.mode not in ("RGB", "RGBA"):
            work = img.convert("RGB")

        save_kwargs: dict[str, Any] = {}
        if target_format in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality

        output = BytesIO()
        work.save(output, format=target_format, **save_kwargs)
        output.seek(0)

        return {
            "success": True,
            "original_format": img.format,
            "original_mode": img.mode,
            "new_format": target_format,
            "quality": quality if target_format in ("JPEG", "WEBP") else None,
            "output_size_bytes": len(output.getvalue()),
            "output_data": output.getvalue(),
        }
