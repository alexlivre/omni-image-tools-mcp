"""Crop image tool for omni-image-tools-mcp."""

from PIL import Image
from typing import Any


async def crop_image(
    image_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> dict[str, Any]:
    """Crop a specific region from an image.

    Args:
        image_path: Path to the image file
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of crop region
        height: Height of crop region

    Returns:
        Dict with cropped image data and info
    """
    img = Image.open(image_path)

    original_width, original_height = img.size

    if x < 0 or y < 0 or x + width > original_width or y + height > original_height:
        return {
            "success": False,
            "error": f"Crop region ({x}, {y}, {width}, {height}) is outside image bounds ({original_width}x{original_height})",
        }

    cropped = img.crop((x, y, x + width, y + height))

    from io import BytesIO

    output = BytesIO()
    cropped.save(output, format=img.format or "PNG")
    output.seek(0)

    return {
        "success": True,
        "original_size": (original_width, original_height),
        "crop_region": {"x": x, "y": y, "width": width, "height": height},
        "cropped_size": (width, height),
        "output_data": output.getvalue(),
    }
