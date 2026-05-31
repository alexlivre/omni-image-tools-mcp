"""Identify objects tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


async def identify_objects(
    image_path: str,
    include_count: bool = False,
    include_location: bool = False,
    categories: str | None = None,
    min_confidence: float = 0.5,
) -> dict[str, Any]:
    """Identify and locate objects in an image.

    Args:
        image_path: Path to the image file
        include_count: Include count of each object type
        include_location: Include approximate location in image
        categories: Filter by categories (comma-separated)
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        Dict with identified objects
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt_parts = []

    if include_count:
        prompt_parts.append(get_vision_prompt("identify_objects", "with_count"))
    else:
        prompt_parts.append(get_vision_prompt("identify_objects", "default"))

    if categories:
        prompt_parts.append(f"Focus on these categories: {categories}")

    prompt_parts.append(f"(Confidence threshold: {min_confidence:.0%})")

    prompt = " ".join(prompt_parts)

    await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.analyze(image_data, prompt)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "options": {
            "include_count": include_count,
            "include_location": include_location,
            "categories": categories,
            "min_confidence": min_confidence,
        },
    }
