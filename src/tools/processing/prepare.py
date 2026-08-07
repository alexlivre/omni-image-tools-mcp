"""Prepare image tool for omni-image-tools-mcp."""

import io
from typing import Any

from PIL import Image


async def prepare_image(
    image_path: str,
    max_width: int = 1024,
    max_height: int = 1024,
    format: str = "JPEG",
    quality: int = 85,
) -> dict[str, Any]:
    """Prepare an image for analysis by resizing and optimizing.

    Args:
        image_path: Path to the image file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        format: Output format (JPEG, PNG, WEBP)
        quality: Quality (1-100)

    Returns:
        Dict with prepared image info and size
    """
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        scale = min(max_width / original_width, max_height / original_height)

        work: Image.Image = img
        if scale < 1:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            work = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if format == "JPEG" and work.mode == "RGBA":
            work = work.convert("RGB")

        output = io.BytesIO()
        work.save(output, format=format, quality=quality)
        output.seek(0)

        return {
            "success": True,
            "original_size": (original_width, original_height),
            "new_size": work.size,
            "format": format,
            "quality": quality,
            "output_size_bytes": len(output.getvalue()),
            "output_data": output.getvalue(),
        }
