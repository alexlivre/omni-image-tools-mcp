"""Extract object from image tool for omni-image-tools-mcp."""

import json
import re
import uuid
from pathlib import Path
from typing import Any

from PIL import Image

from ...config import get_config
from ...providers import ProviderFactory
from ...utils.gpu_memory import GPUResourceManager


async def extract_object(
    image_path: str,
    object_description: str,
    output_filename: str | None = None,
) -> dict[str, Any]:
    """Locate and crop an object from an image.

    Finds the specified object in the image using AI vision,
    then crops and saves the region containing it.

    Args:
        image_path: Path to the image file
        object_description: Description of the object to locate and extract
        output_filename: Filename for the extracted image (optional)

    Returns:
        Dict with local_path, coordinates, format, size
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    with open(image_path, "rb") as f:
        image_data = f.read()

    img = Image.open(image_path)
    img_width, img_height = img.size

    await GPUResourceManager.ensure_single_provider(config.provider)

    locate_prompt = (
        f'Locate the "{object_description}" in this image. '
        f"Output EXACTLY this JSON format with the bounding box coordinates, nothing else:\n"
        f'{{"bbox_2d": [x1, y1, x2, y2]}}\n'
        f"Where coordinates are normalized to 0-1000 range. "
        f"[x1,y1] is top-left, [x2,y2] is bottom-right."
    )

    result_text = await provider.analyze(image_data, locate_prompt, None)

    coords = _parse_coordinates(result_text)

    if not coords:
        return {
            "success": False,
            "error": f"Could not locate '{object_description}' in the image",
            "result_text": result_text,
        }

    x1_norm, y1_norm, x2_norm, y2_norm = coords

    x1 = max(0, int((x1_norm / 1000) * img_width))
    y1 = max(0, int((y1_norm / 1000) * img_height))
    x2 = min(img_width, int((x2_norm / 1000) * img_width))
    y2 = min(img_height, int((y2_norm / 1000) * img_height))

    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    if x2 - x1 < 5 or y2 - y1 < 5:
        return {
            "success": False,
            "error": f"Extracted region too small ({x2-x1}x{y2-y1}px). Object may not be visible.",
            "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "image_size": (img_width, img_height),
        }

    cropped = img.crop((x1, y1, x2, y2))
    ext = Path(image_path).suffix if Path(image_path).suffix else ".jpg"

    if output_filename:
        save_name = output_filename
        if not save_name.endswith(ext) and not save_name.endswith(".png") and not save_name.endswith(".jpg"):
            save_name += ext
    else:
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', object_description)[:30]
        save_name = f"{safe_name}_{uuid.uuid4().hex[:6]}{ext}"

    save_dir = Path(__file__).parent.parent.parent.parent / "test_images"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / save_name
    cropped.save(save_path)

    return {
        "success": True,
        "local_path": str(save_path),
        "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "object_description": object_description,
        "extracted_size": cropped.size,
        "original_size": (img_width, img_height),
        "format": cropped.format or "JPEG",
    }


def _parse_coordinates(text: str) -> list[int] | None:
    """Parse bounding box coordinates from model response."""
    try:
        data = json.loads(text)
        bbox = data.get("bbox_2d")
        if bbox and len(bbox) == 4:
            return [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    match = re.search(r'bbox_2d["\']?\s*:\s*\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]', text)
    if match:
        return [int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))]

    match = re.search(r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]', text)
    if match:
        return [int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))]

    return None
