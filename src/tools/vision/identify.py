"""Identify objects tool for omni-image-tools-mcp."""

import hashlib
from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils import preprocess_to_bytes
from ...utils.gpu_memory import GPUResourceManager
from ...utils.result_cache import cache_result, cached, make_key

_CACHE_TOOL = "identify_objects"


async def identify_objects(
    image_path: str,
    include_count: bool = False,
    categories: str | None = None,
    min_confidence: float = 0.5,
) -> dict[str, Any]:
    """Identify and locate objects in an image.

    Args:
        image_path: Path to the image file
        include_count: Include count of each object type
        categories: Filter by categories (comma-separated)
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        Dict with identified objects
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    image_data = preprocess_to_bytes(image_path)
    image_sha = hashlib.sha256(image_data).hexdigest()

    prompt_parts = []

    if include_count:
        prompt_parts.append(get_vision_prompt("identify_objects", "with_count"))
    else:
        prompt_parts.append(get_vision_prompt("identify_objects", "default"))

    if categories:
        prompt_parts.append(f"Focus on these categories: {categories}")

    prompt_parts.append(f"(Confidence threshold: {min_confidence:.0%})")

    prompt = " ".join(prompt_parts)

    effective_model = config.default_model or "unknown"
    key = make_key(_CACHE_TOOL, image_sha, prompt, effective_model)

    cached_result = cached(key)
    if cached_result is not None:
        return {
            "success": True,
            "result": cached_result,
            "provider": config.provider,
            "options": {
                "include_count": include_count,
                "categories": categories,
                "min_confidence": min_confidence,
            },
            "cached": True,
        }

    await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.analyze(image_data, prompt)
    cache_result(key, result)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "options": {
            "include_count": include_count,
            "categories": categories,
            "min_confidence": min_confidence,
        },
    }
