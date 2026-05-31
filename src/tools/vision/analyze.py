"""Analyze image tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


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

    with open(image_path, "rb") as f:
        image_data = f.read()

    if prompt is None:
        prompt = get_vision_prompt("analyze_image", detail_level)

    gpu_status = await GPUResourceManager.check_for_provider(config.provider, model)
    result = await provider.analyze(image_data, prompt, model)

    response = {
        "success": True,
        "result": result,
        "provider": config.provider,
        "model": model or config.default_model or "unknown",
    }

    if gpu_status["warnings"]:
        response["gpu_warnings"] = gpu_status["warnings"]

    return response
