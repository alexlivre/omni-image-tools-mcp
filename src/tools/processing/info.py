"""Get image info tool for omni-image-tools-mcp."""

from PIL import Image
import exifread
from typing import Any


async def get_image_info(
    image_path: str,
    include_exif: bool = True,
) -> dict[str, Any]:
    """Get metadata information about an image.

    Args:
        image_path: Path to the image file
        include_exif: Include EXIF metadata

    Returns:
        Dict with image metadata
    """
    img = Image.open(image_path)

    info = {
        "success": True,
        "format": img.format,
        "mode": img.mode,
        "size": {
            "width": img.width,
            "height": img.height,
        },
        "has_transparency": img.mode in ("RGBA", "LA", "P"),
    }

    if hasattr(img, "_getexif") and img._getexif():
        exif_data = img._getexif()
        if exif_data:
            info["exif_available"] = True

    if include_exif:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f)
            if tags:
                info["exif"] = {tag: str(value) for tag, value in tags.items()}

    return info
