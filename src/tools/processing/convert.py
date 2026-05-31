"""Convert image format tool for omni-image-tools-mcp."""

from PIL import Image
from io import BytesIO
from typing import Any


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
    img = Image.open(image_path)

    format_map = {
        "JPEG": "JPEG",
        "JPG": "JPEG",
        "PNG": "PNG",
        "WEBP": "WEBP",
        "BMP": "BMP",
        "GIF": "GIF",
    }

    target_format = format_map.get(output_format.upper())
    if not target_format:
        return {
            "success": False,
            "error": f"Unsupported format: {output_format}. Supported: JPEG, PNG, WEBP, BMP, GIF",
        }

    if target_format == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")
    elif target_format == "PNG" and img.mode == "RGB":
        pass
    elif target_format not in ("RGB", "RGBA") and img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    output = BytesIO()

    save_kwargs = {}
    if target_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality

    img.save(output, format=target_format, **save_kwargs)
    output.seek(0)

    result_size = len(output.getvalue())

    return {
        "success": True,
        "original_format": img.format,
        "original_mode": img.mode,
        "new_format": target_format,
        "quality": quality,
        "output_size_bytes": result_size,
        "output_data": output.getvalue(),
    }
