"""Get image info tool for omni-image-tools-mcp."""

from typing import Any

import exifread
from PIL import Image

_GPS_TAGS = ("GPS GPSLatitude", "GPS GPSLongitude", "GPS GPSAltitude")


async def get_image_info(
    image_path: str,
    include_exif: bool = False,
) -> dict[str, Any]:
    """Get metadata information about an image.

    EXIF is off by default for privacy (it may contain GPS location). When
    enabled and GPS tags are present, a privacy warning is included.

    Args:
        image_path: Path to the image file
        include_exif: Include EXIF metadata (default off for privacy)

    Returns:
        Dict with image metadata
    """
    with Image.open(image_path) as img:
        info: dict[str, Any] = {
            "success": True,
            "format": img.format,
            "mode": img.mode,
            "size": {
                "width": img.width,
                "height": img.height,
            },
            "has_transparency": img.mode in ("RGBA", "LA", "P"),
        }

    if include_exif:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f)
        if tags:
            exif_map: dict[str, str] = {}
            for tag, value in tags.items():
                exif_map[str(tag)] = str(value)
            info["exif"] = exif_map
            if any(tag in tags for tag in _GPS_TAGS):
                info["exif_privacy_warning"] = (
                    "EXIF contains GPS coordinates that may reveal location."
                )

    return info
