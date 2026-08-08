"""Analyze image tool for omni-image-tools-mcp."""

import hashlib
from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils import preprocess_to_bytes
from ...utils.gpu_memory import GPUResourceManager
from ...utils.result_cache import cache_result, cached, make_key

_CACHE_TOOL = "analyze_image"


async def analyze_image(
    image_path: str,
    prompt: str | None = None,
    model: str | None = None,
    detail_level: str = "standard",
) -> dict[str, Any]:
    """Analyze an image with a custom prompt.

    Args:
        image_path: Path to the image file
        prompt: Custom prompt/question about the image
        model: Model to use (optional)
        detail_level: Level of detail (brief, standard, detailed)

    Returns:
        Dict with analysis result
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    image_data = preprocess_to_bytes(image_path)
    image_sha = hashlib.sha256(image_data).hexdigest()

    if prompt is None:
        prompt = get_vision_prompt("analyze_image", detail_level)

    effective_model = model or config.default_model or "unknown"
    key = make_key(_CACHE_TOOL, image_sha, prompt, effective_model)

    cached_result = cached(key)
    if cached_result is not None:
        return {
            "success": True,
            "result": cached_result,
            "provider": config.provider,
            "model": effective_model,
            "cached": True,
        }

    await GPUResourceManager.ensure_single_provider(config.provider, model)
    result = await provider.analyze(image_data, prompt, model)
    cache_result(key, result)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "model": effective_model,
    }
