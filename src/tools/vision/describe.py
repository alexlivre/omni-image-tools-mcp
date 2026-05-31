"""Describe image tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


async def describe_image(
    image_path: str,
    description_type: str = "detailed",
) -> dict[str, Any]:
    """Get a description of what an image contains.

    Args:
        image_path: Path to the image file
        description_type: Type of description (simple, detailed, verbose)

    Returns:
        Dict with description result
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt = get_vision_prompt("describe_image", description_type)

    gpu_status = await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.analyze(image_data, prompt)

    response = {
        "success": True,
        "result": result,
        "provider": config.provider,
        "description_type": description_type,
    }

    if gpu_status["warnings"] or gpu_status["unloaded"]:
        response["gpu_status"] = {
            "status": gpu_status["status"],
            "unloaded": gpu_status["unloaded"],
            "warnings": gpu_status["warnings"],
        }

    return response
