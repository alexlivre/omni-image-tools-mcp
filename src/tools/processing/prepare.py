"""Prepare image tool for omni-image-tools-mcp."""

import io
from PIL import Image
from typing import Any


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
    img = Image.open(image_path)

    original_width, original_height = img.size
    scale = min(max_width / original_width, max_height / original_height)

    if scale < 1:
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    if format == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")

    output = io.BytesIO()
    img.save(output, format=format, quality=quality)
    output.seek(0)

    result_size = len(output.getvalue())

    return {
        "success": True,
        "original_size": (original_width, original_height),
        "new_size": img.size,
        "format": format,
        "quality": quality,
        "output_size_bytes": result_size,
        "output_data": output.getvalue(),
    }
