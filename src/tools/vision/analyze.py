"""Analyze image tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt


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

    result = await provider.analyze(image_data, prompt, model)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "model": model or config.default_model or "unknown",
    }
